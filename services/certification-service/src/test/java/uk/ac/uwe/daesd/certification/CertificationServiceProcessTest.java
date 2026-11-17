package uk.ac.uwe.daesd.certification;

import static io.camunda.zeebe.process.test.assertions.BpmnAssert.assertThat;

import io.camunda.zeebe.client.ZeebeClient;
import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.client.api.response.ProcessInstanceEvent;
import io.camunda.zeebe.process.test.api.ZeebeTestEngine;
import io.camunda.zeebe.process.test.extension.ZeebeProcessTest;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Integration tests: the real certification service handler answers Omar's real F1 process
 * (camunda/processes/product-listing-publication.bpmn) on an embedded Zeebe engine.
 * Covers the three organic routes that depend on this service.
 */
@ZeebeProcessTest
class CertificationServiceProcessTest {

  private static final Path CAMUNDA = Path.of("..", "..", "camunda");
  private static final String USER_TASK_JOB = "io.camunda.zeebe:userTask";

  private ZeebeTestEngine engine;
  private ZeebeClient client;
  private CertificationJobHandler service;

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
    service = new CertificationJobHandler(client, new CertificationRegistry(), Duration.ZERO);
  }

  @Test
  void verifiedCertificatePublishesTheProductAsOrganic() {
    var instance = submitOrganicProduct("GB-ORG-05");
    serviceHandlesRequest();

    assertThat(instance).isCompleted()
        .hasPassedElement("Task_RecordVerified")
        .hasPassedElement("End_Published")
        .hasVariableWithValue("certificationVerified", true)
        .hasVariableWithValue("organicStatus", "Verified organic");
  }

  @Test
  void rejectedCertificateAsksTheProducerWhatToDo() {
    var instance = submitOrganicProduct("GB-ORG-99");
    serviceHandlesRequest();

    assertThat(instance).isWaitingAtElements("Task_RejectedDecision")
        .hasPassedElement("Task_FlagRejected")
        .hasVariableWithValue("certificationVerified", false);
  }

  @Test
  void unavailableServiceIsRetriedThreeTimesThenSentToManualReview() throws Exception {
    var instance = submitOrganicProduct("GB-ORG-00");
    for (int attempt = 1; attempt <= 3; attempt++) {
      serviceHandlesRequest();
      assertThat(instance).isActive().hasNotPassedElement("Task_RecordVerified");
      engine.increaseTime(Duration.ofSeconds(31));
      idle();
    }

    assertThat(instance).isWaitingAtElements("Task_ReviewEvidence")
        .hasPassedElement("Task_FlagManualReview")
        .hasVariableWithValue("certificationAttempts", 3)
        .hasVariableWithValue("listingStatus", "Pending manual review");
  }

  @Test
  void anyOtherUkOrganicCodeIsVerified() {
    var instance = submitOrganicProduct("GB-ORG-13");
    serviceHandlesRequest();

    assertThat(instance).isCompleted()
        .hasPassedElement("End_Published")
        .hasVariableWithValue("organicStatus", "Verified organic");
  }

  // ---------------------------------------------------------------- helpers

  private ProcessInstanceEvent submitOrganicProduct(String certificationReference) {
    var instance = client.newCreateInstanceCommand()
        .bpmnProcessId("product-listing-publication").latestVersion().send().join();
    idle();
    var product = organicProduct(certificationReference);
    ActivatedJob form = activateOne(USER_TASK_JOB, "Task_SubmitDetails");
    client.newCompleteCommand(form.getKey()).variables(product).send().join();
    idle();
    return instance;
  }

  /** Activates the certification job exactly as the running worker would, and passes it to the service. */
  private void serviceHandlesRequest() {
    ActivatedJob job = activateOne(CertificationJobHandler.JOB_TYPE, null);
    service.handle(client, job);
    idle();
  }

  private Map<String, Object> organicProduct(String certificationReference) {
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
    p.put("organicClaimMade", true);
    p.put("certificationReference", certificationReference);
    return p;
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

  /** Same approach as tests/camunda-f1: the embedded engine completes user tasks as jobs. */
  private static byte[] withJobBasedUserTasks(String file) throws IOException {
    return Files.readString(CAMUNDA.resolve(file)).replaceAll("<zeebe:userTask\\s*/>", "").getBytes(StandardCharsets.UTF_8);
  }
}
