package uk.ac.uwe.daesd;

import static io.camunda.zeebe.process.test.assertions.BpmnAssert.assertThat;
import io.camunda.zeebe.client.ZeebeClient;
import io.camunda.zeebe.client.api.response.ProcessInstanceEvent;
import io.camunda.zeebe.process.test.api.ZeebeTestEngine;
import io.camunda.zeebe.process.test.extension.ZeebeProcessTest;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import org.junit.jupiter.api.*;

/** Executes canonical ordering gateway routes. Services and native user tasks are test doubles. */
@ZeebeProcessTest
class OrderingProcessTest {
  private ZeebeTestEngine engine;
  private ZeebeClient client;
  @BeforeEach void deploy() throws Exception {
    var folder=Path.of("..","..","camunda","f2");
    var deployment=client.newDeployResourceCommand().addResourceFile(folder.resolve("processes/check-product-stock-status.bpmn").toString());
    for(var name:new String[]{"place-order-horizontal.bpmn"}) {
      var xml=Files.readString(folder.resolve("processes").resolve(name));
      deployment=deployment.addResourceBytes(xml.replaceAll("<zeebe:userTask\\s*/>", "").getBytes(StandardCharsets.UTF_8),name);
    }
    try(var files=Files.list(folder.resolve("forms"))) {
      for(var file:files.toList()) deployment=deployment.addResourceFile(file.toString());
    }
    deployment.send().join();
  }
  void idle() throws Exception {engine.waitForIdleState(Duration.ofSeconds(5));}
  void complete(String type,Map<String,Object> vars) throws Exception {
    var jobs=client.newActivateJobsCommand().jobType(type).maxJobsToActivate(1).send().join().getJobs();
    org.assertj.core.api.Assertions.assertThat(jobs).hasSize(1);
    client.newCompleteCommand(jobs.getFirst().getKey()).variables(vars).send().join();idle();
  }
  ProcessInstanceEvent order(boolean valid) throws Exception {
    var instance=client.newCreateInstanceCommand().bpmnProcessId("f2_customer_ordering").latestVersion().send().join();idle();
    complete("f2-prepare-order",Map.of("orderId","TEST-ORDER","productOptions",java.util.List.of()));
    assertThat(instance).isWaitingAtElements("Order");
    complete("io.camunda.zeebe:userTask",Map.of("productId","P1","purchasedQuantity",3,"customerName","Synthetic test","customerEmail","test@example.com"));
    complete("f2-validate-order",Map.of("orderValid",valid,"orderAccepted",false,"paymentStatus","Not authorized"));
    return instance;
  }
  void authorize(boolean approved) throws Exception {
    complete("io.camunda.zeebe:userTask",Map.of("demoPaymentOutcome",approved?"approve":"decline"));
    complete("f2-authorize-payment",Map.of("paymentAuthorized",approved,"paymentStatus",approved?"authorized":"declined"));
  }
  @Test void successfulOrderCapturesAndUsesOriginalLowStockNotification() throws Exception {
    var instance=order(true);authorize(true);
    complete("f2-commit-order",Map.of("orderAccepted",true,"quantity",1,"withinSeason",true,"lowStockThreshold",2));
    complete("f2-settle-payment",Map.of("paymentStatus","captured","paymentAuthorized",true));
    complete("f2-available",Map.of());complete("f2-notify-low",Map.of());complete("f2-save-final",Map.of());
    assertThat(instance).isWaitingAtElements("Result");complete("io.camunda.zeebe:userTask",Map.of());
    assertThat(instance).isCompleted().hasPassedElement("Capture").hasPassedElement("Activity_0a0msio").hasNotPassedElement("Void");
  }
  @Test void lastItemTriggersOutOfStockNotification() throws Exception {
    var instance=order(true);authorize(true);
    complete("f2-commit-order",Map.of("orderAccepted",true,"quantity",0,"withinSeason",true,"lowStockThreshold",2));
    complete("f2-settle-payment",Map.of("paymentStatus","captured","paymentAuthorized",true));
    complete("f2-unavailable",Map.of());complete("f2-notify-zero",Map.of());complete("f2-save-final",Map.of());
    complete("io.camunda.zeebe:userTask",Map.of());
    assertThat(instance).isCompleted().hasPassedElement("Activity_1knv4gv").hasNotPassedElement("Activity_0a0msio");
  }
  @Test void declinedPaymentCannotCommitStock() throws Exception {
    var instance=order(true);authorize(false);complete("io.camunda.zeebe:userTask",Map.of());
    assertThat(instance).isCompleted().hasPassedElement("Reject").hasNotPassedElement("Activity_0wf1ny8").hasNotPassedElement("Capture");
  }
  @Test void insufficientStockIsRejectedBeforePayment() throws Exception {
    var instance=order(false);complete("io.camunda.zeebe:userTask",Map.of());
    assertThat(instance).isCompleted().hasPassedElement("Reject").hasNotPassedElement("Authorize").hasNotPassedElement("Activity_0wf1ny8");
  }
  @Test void stockRaceVoidsAuthorization() throws Exception {
    var instance=order(true);authorize(true);
    complete("f2-commit-order",Map.of("orderAccepted",false));
    complete("f2-settle-payment",Map.of("paymentStatus","voided","paymentAuthorized",false));
    complete("io.camunda.zeebe:userTask",Map.of());
    assertThat(instance).isCompleted().hasPassedElement("Void").hasNotPassedElement("Capture").hasNotPassedElement("Activity_0kb95hx");
  }
}
