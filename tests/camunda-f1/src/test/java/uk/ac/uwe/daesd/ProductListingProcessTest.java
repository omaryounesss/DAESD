package uk.ac.uwe.daesd;

import static io.camunda.zeebe.process.test.assertions.BpmnAssert.assertThat;
import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.camunda.zeebe.client.ZeebeClient;
import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.client.api.response.ProcessInstanceEvent;
import io.camunda.zeebe.process.test.api.ZeebeTestEngine;
import io.camunda.zeebe.process.test.extension.ZeebeProcessTest;
import io.camunda.zeebe.process.test.filters.RecordStream;
import io.camunda.zeebe.protocol.record.Record;
import io.camunda.zeebe.protocol.record.value.VariableRecordValue;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Runs every Functionality 1 route through the real files in camunda/ on an embedded Zeebe engine.
 * The test plays the producer, the administrator and the simulated certification service.
 */
@ZeebeProcessTest
class ProductListingProcessTest {

  private static final Path CAMUNDA = Path.of("..", "..", "camunda");
  private static final String USER_TASK_JOB = "io.camunda.zeebe:userTask";
  private static final String CERTIFICATION_JOB = "request-certification-verification";
  private static final ObjectMapper JSON = new ObjectMapper();

  private ZeebeTestEngine engine;
  private ZeebeClient client;
  private RecordStream recordStream;

  @BeforeEach
  void deploy() throws Exception {
    var deployment = client.newDeployResourceCommand()
        .addResourceBytes(withJobBasedUserTasks("processes/product-listing-publication.bpmn"), "product-listing-publication.bpmn")
        .addResourceBytes(withJobBasedUserTasks("processes/record-product-traceability.bpmn"), "record-product-traceability.bpmn");
    try (var forms = Files.list(CAMUNDA.resolve("forms"))) {
      for (Path form : forms.toList()) {
        deployment = deployment.addResourceFile(form.toString());
      }
    }
    deployment.send().join();
  }

  // ------------------------------------------------------------------ routes

  @Test
  void validNonOrganicProductIsPublished() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", validProduct());

    assertThat(instance).isCompleted()
        .hasPassedElement("SubProcess_ValidateDetails")
        .hasPassedElement("Call_RecordTraceability")
        .hasPassedElement("End_Published")
        .hasNotPassedElement("Task_RequestCertification")
        .hasVariableWithValue("listingStatus", "Published")
        .hasVariableWithValue("productDetailsValid", true);
    assertThat(this.<String>variable(instance, "listingId")).startsWith("LST-");
    assertThat(this.<Map<String, Object>>variable(instance, "traceabilityRecord"))
        .containsEntry("origin", "Ashton Court Farm, Bristol")
        .containsEntry("allergens", "None")
        .containsEntry("producerName", "Ashton Court Farm");
    assertThat(notificationTypes(instance)).containsExactly("listing-published");
  }

  @Test
  void invalidProductIsCorrectedAndRevalidated() {
    var instance = start();
    var invalid = validProduct();
    invalid.put("price", 0);
    invalid.put("harvestDate", LocalDate.now().plusDays(3).toString());
    invalid.put("bestBeforeDate", LocalDate.now().plusDays(1).toString());
    invalid.put("availableUntil", LocalDate.now().minusMonths(2).toString());
    invalid.put("origin", "");
    completeUserTask("Task_SubmitDetails", invalid);

    assertThat(instance).isWaitingAtElements("Task_CorrectDetails")
        .hasPassedElement("Task_RequestCorrections")
        .hasVariableWithValue("productDetailsValid", false);
    assertThat(this.<List<Object>>variable(instance, "validationErrors")).containsExactlyInAnyOrder(
        "Farm origin is required.",
        "Price must be greater than zero.",
        "Availability end date must be on or after the start date.",
        "Harvest date cannot be in the future.",
        "Best-before date must be after the harvest date.");

    completeUserTask("Task_CorrectDetails", validProduct());

    assertThat(instance).isCompleted().hasPassedElement("End_Published");
    assertThat(this.<List<Object>>variable(instance, "validationErrors")).isEmpty();
    assertThat(notificationTypes(instance)).containsExactly("correction-requested", "listing-published");
  }

  @Test
  void missingMandatoryFieldsAreReported() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", Map.of("productName", "Leeks", "organicClaimMade", false));

    assertThat(instance).isWaitingAtElements("Task_CorrectDetails");
    assertThat(this.<List<Object>>variable(instance, "validationErrors")).contains(
        "Producer name is required.", "Price is required.", "Quantity is required.",
        "Harvest date is required.", "Availability end date is required.");
  }

  @Test
  void organicClaimNeedsAValidCertificationReference() {
    var instance = start();
    var product = validProduct();
    product.put("organicClaimMade", true);
    product.put("certificationReference", "SOIL-123");
    completeUserTask("Task_SubmitDetails", product);

    assertThat(instance).isWaitingAtElements("Task_CorrectDetails");
    assertThat(this.<List<Object>>variable(instance, "validationErrors")).containsExactly(
        "Certification reference must be a UK organic control body code, e.g. GB-ORG-05.");
  }

  @Test
  void verifiedOrganicClaimIsPublishedAsOrganic() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    certificationServiceReplies("verified");

    assertThat(instance).isCompleted()
        .hasPassedElement("Task_RecordVerified")
        .hasPassedElement("End_Published")
        .hasVariableWithValue("certificationVerified", true)
        .hasVariableWithValue("organicStatus", "Verified organic");
    assertThat(this.<Map<String, Object>>variable(instance, "product")).containsEntry("organic", true);
    assertThat(this.<Map<String, Object>>variable(instance, "traceabilityRecord")).containsEntry("certificationReference", "GB-ORG-05");
  }

  @Test
  void rejectedClaimCanBeRemovedAndListingPublished() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    certificationServiceReplies("rejected");

    assertThat(instance).isWaitingAtElements("Task_RejectedDecision")
        .hasPassedElement("Task_FlagRejected")
        .hasPassedElement("Task_NotifyRejected");
    completeUserTask("Task_RejectedDecision", Map.of("rejectedClaimDecision", "remove-claim"));

    assertThat(instance).isCompleted()
        .hasPassedElement("Task_RemoveClaim")
        .hasPassedElement("End_Published")
        .hasVariableWithValue("certificationVerified", false)
        .hasVariableWithValue("removeOrganicClaim", true)
        .hasVariableWithValue("organicClaimMade", false);
    assertThat(this.<Map<String, Object>>variable(instance, "product"))
        .containsEntry("organic", false).containsEntry("organicStatus", "Not organic");
  }

  @Test
  void rejectedClaimCanBeWithheld() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    certificationServiceReplies("rejected");
    completeUserTask("Task_RejectedDecision", Map.of("rejectedClaimDecision", "withhold"));

    assertThat(instance).isCompleted()
        .hasPassedElement("End_WithheldRejected")
        .hasNotPassedElement("Task_PublishListing")
        .hasVariableWithValue("listingStatus", "Withheld");
    assertThat(notificationTypes(instance)).containsExactly("organic-claim-rejected", "listing-withheld");
  }

  @Test
  void unavailableServiceIsRetriedThenManuallyApproved() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    serviceUnavailableThreeTimes();

    assertThat(instance).isWaitingAtElements("Task_ReviewEvidence")
        .hasPassedElement("Task_FlagManualReview")
        .hasVariableWithValue("certificationAttempts", 3)
        .hasVariableWithValue("listingStatus", "Pending manual review");
    completeManualReview("approve");

    assertThat(instance).isCompleted()
        .hasPassedElement("Task_RecordManualVerified")
        .hasPassedElement("End_Published")
        .hasNotPassedElement("Task_FlagOverdue")
        .hasVariableWithValue("manualCertificationVerified", true)
        .hasVariableWithValue("organicStatus", "Verified organic (manual review)")
        .hasVariableWithValue("listingStatus", "Published");
  }

  @Test
  void manualReviewCanWithholdListing() {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    serviceUnavailableThreeTimes();
    completeManualReview("reject");

    assertThat(instance).isCompleted()
        .hasPassedElement("End_WithheldManual")
        .hasNotPassedElement("Task_PublishListing")
        .hasVariableWithValue("listingStatus", "Withheld");
  }

  @Test
  void overdueManualReviewIsEscalatedWithoutCancellingIt() throws Exception {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    serviceUnavailableThreeTimes();

    engine.increaseTime(Duration.ofHours(25));
    engine.waitForIdleState(Duration.ofSeconds(5));

    assertThat(instance).isActive()
        .hasPassedElement("Task_FlagOverdue")
        .hasPassedElement("End_EscalationRecorded")
        .isWaitingAtElements("Task_ReviewEvidence")
        .hasVariableWithValue("manualReviewOverdue", true);

    completeManualReview("approve");
    assertThat(instance).isCompleted().hasPassedElement("End_Published");
  }

  @Test
  void lateRecoveryAfterOneTimeoutStillVerifies() throws Exception {
    var instance = start();
    completeUserTask("Task_SubmitDetails", organicProduct());
    certificationServiceReplies("unavailable");
    engine.increaseTime(Duration.ofSeconds(31));
    engine.waitForIdleState(Duration.ofSeconds(5));
    certificationServiceReplies("verified");

    assertThat(instance).isCompleted()
        .hasPassedElement("End_Published")
        .hasVariableWithValue("certificationAttempts", 1)
        .hasVariableWithValue("organicStatus", "Verified organic");
  }

  // ---------------------------------------------------------------- helpers

  private ProcessInstanceEvent start() {
    var instance = client.newCreateInstanceCommand()
        .bpmnProcessId("product-listing-publication").latestVersion().send().join();
    idle();
    return instance;
  }

  private Map<String, Object> validProduct() {
    var p = new HashMap<String, Object>();
    p.put("producerName", "Ashton Court Farm");
    p.put("productName", "Heritage carrots");
    p.put("productDescription", "Mixed colour carrots, 1 kg bag");
    p.put("category", "Vegetables");
    p.put("price", 2.5);
    p.put("quantity", 40);
    p.put("availableFrom", LocalDate.now().minusMonths(1).toString());
    p.put("availableUntil", LocalDate.now().plusMonths(2).toString());
    p.put("origin", "Ashton Court Farm, Bristol");
    p.put("harvestDate", LocalDate.now().minusDays(2).toString());
    p.put("bestBeforeDate", LocalDate.now().plusDays(12).toString());
    p.put("allergens", "None");
    p.put("organicClaimMade", false);
    return p;
  }

  private Map<String, Object> organicProduct() {
    var p = validProduct();
    p.put("organicClaimMade", true);
    p.put("certificationReference", "GB-ORG-05");
    return p;
  }

  /** Simulated certification service: takes the request job, then replies (or stays silent if unavailable). */
  private void certificationServiceReplies(String status) {
    ActivatedJob job = activateOne(CERTIFICATION_JOB, null);
    String listingId = (String) job.getVariablesAsMap().get("listingId");
    client.newCompleteCommand(job.getKey()).send().join();
    idle();
    if (!status.equals("unavailable")) {
      client.newPublishMessageCommand().messageName("certification-result").correlationKey(listingId)
          .variables(Map.of("certificationStatus", status)).send().join();
      idle();
    }
  }

  private void serviceUnavailableThreeTimes() {
    for (int attempt = 0; attempt < 3; attempt++) {
      certificationServiceReplies("unavailable");
      try {
        engine.increaseTime(Duration.ofSeconds(31));
        engine.waitForIdleState(Duration.ofSeconds(5));
      } catch (Exception e) {
        throw new IllegalStateException(e);
      }
    }
  }

  private void completeManualReview(String decision) {
    completeUserTask("Task_ReviewEvidence", Map.of("certificateDocumentSeen", true, "evidenceReviewNotes", "PDF certificate supplied"));
    completeUserTask("Task_CheckProducerDetails", Map.of("producerNameMatchesCertificate", true, "certificateInDate", true));
    completeUserTask("Task_RecordReviewDecision", Map.of("manualReviewDecision", decision, "manualReviewNotes", "Checked against register"));
  }

  private void completeUserTask(String elementId, Map<String, Object> variables) {
    ActivatedJob job = activateOne(USER_TASK_JOB, elementId);
    client.newCompleteCommand(job.getKey()).variables(variables).send().join();
    idle();
  }

  private ActivatedJob activateOne(String type, String elementId) {
    var jobs = client.newActivateJobsCommand().jobType(type).maxJobsToActivate(10).send().join().getJobs();
    return jobs.stream()
        .filter(j -> elementId == null || j.getElementId().equals(elementId))
        .findFirst()
        .orElseThrow(() -> new AssertionError("No active job of type " + type + " at " + elementId));
  }

  private void idle() {
    try {
      engine.waitForIdleState(Duration.ofSeconds(5));
    } catch (Exception e) {
      throw new IllegalStateException(e);
    }
  }

  /** Latest value of a process-level variable, parsed from JSON. */
  @SuppressWarnings("unchecked")
  private <T> T variable(ProcessInstanceEvent instance, String name) {
    Record<VariableRecordValue> last = StreamSupport.stream(recordStream.variableRecords().spliterator(), false)
        .filter(r -> r.getValue().getProcessInstanceKey() == instance.getProcessInstanceKey())
        .filter(r -> r.getValue().getScopeKey() == instance.getProcessInstanceKey())
        .filter(r -> r.getValue().getName().equals(name))
        .reduce((a, b) -> b)
        .orElseThrow(() -> new AssertionError("Variable not set: " + name));
    try {
      return (T) JSON.readValue(last.getValue().getValue(), Object.class);
    } catch (IOException e) {
      throw new IllegalStateException(e);
    }
  }

  private List<Object> notificationTypes(ProcessInstanceEvent instance) {
    return (this.<List<Object>>variable(instance, "producerNotifications")).stream()
        .map(n -> ((Map<?, ?>) n).get("type")).map(Object.class::cast).toList();
  }

  /**
   * The engine embedded in zeebe-process-test completes user tasks as jobs, so the test copy drops the
   * zeebe:userTask marker. The deployed files in camunda/ keep Camunda user tasks for Tasklist.
   */
  private static byte[] withJobBasedUserTasks(String file) throws IOException {
    return Files.readString(CAMUNDA.resolve(file)).replaceAll("<zeebe:userTask\\s*/>", "").getBytes(StandardCharsets.UTF_8);
  }
}
