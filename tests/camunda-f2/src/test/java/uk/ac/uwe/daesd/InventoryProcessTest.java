package uk.ac.uwe.daesd;

import static io.camunda.zeebe.process.test.assertions.BpmnAssert.assertThat;
import io.camunda.zeebe.client.ZeebeClient;
import io.camunda.zeebe.process.test.api.ZeebeTestEngine;
import io.camunda.zeebe.process.test.extension.ZeebeProcessTest;
import java.nio.file.*;
import java.time.Duration;
import java.util.Map;
import org.junit.jupiter.api.*;

@ZeebeProcessTest
class InventoryProcessTest {
  private ZeebeTestEngine engine;
  private ZeebeClient client;
  @BeforeEach void deploy() throws Exception {
    var deployment=client.newDeployResourceCommand().addResourceFile(Path.of("..","..","camunda","f2","processes","check-product-stock-status.bpmn").toString());
    try(var paths=Files.walk(Path.of("..","..","camunda","f2"))) {
      for(var file:paths.filter(Files::isRegularFile).toList()) {
        if(!file.toString().endsWith(".bpmn") && !file.toString().endsWith(".form")) continue;
        if(file.getFileName().toString().equals("check-product-stock-status.bpmn")) continue;
        // Embedded test engine uses job-based user tasks; deployment files keep native Tasklist tasks.
        var bytes=Files.readString(file).replaceAll("<zeebe:userTask\\s*/>", "").getBytes(java.nio.charset.StandardCharsets.UTF_8);
        deployment=deployment.addResourceBytes(bytes,file.getFileName().toString());
      }
    }
    deployment.send().join();
  }
  void idle() throws Exception {engine.waitForIdleState(Duration.ofSeconds(5));}
  void complete(String type,Map<String,Object> vars) throws Exception {
    var jobs=client.newActivateJobsCommand().jobType(type).maxJobsToActivate(1).send().join().getJobs();
    org.assertj.core.api.Assertions.assertThat(jobs).hasSize(1);
    client.newCompleteCommand(jobs.getFirst().getKey()).variables(vars).send().join();idle();
  }
  io.camunda.zeebe.client.api.response.ProcessInstanceEvent update() throws Exception {
    var instance=client.newCreateInstanceCommand().bpmnProcessId("Process_0g8kz9d").latestVersion()
      .startBeforeElement("Event_0yt42mz").variables(Map.of("productId","P1","updateId","U1")).send().join();idle();return instance;
  }
  @Test void validUpdateTraversesOriginalValidationAndAvailableRoute() throws Exception {
    var instance=update();
    complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",true));
    complete("f2-save-update",Map.of("quantity",10,"withinSeason",true,"lowStockThreshold",5));
    complete("f2-available",Map.of("available",true));
    assertThat(instance).isCompleted().hasPassedElement("Activity_0u9a3lc").hasPassedElement("Activity_1ktonrk").hasPassedElement("Event_12htmiz");
  }
  @Test void invalidThirdAttemptWaitsForAdminAndCanBeRejected() throws Exception {
    var instance=update();complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",false,"correctionAttempts",3));
    assertThat(instance).isWaitingAtElements("Activity_07qa1zf");
    complete("io.camunda.zeebe:userTask",Map.of("allowAnotherCorrection",false));
    assertThat(instance).isCompleted().hasPassedElement("Event_0ktx514").hasNotPassedElement("Activity_0t8snic");
  }
  @Test void reviewTimesOutAfter48Hours() throws Exception {
    var instance=update();complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",false,"correctionAttempts",3));
    engine.increaseTime(Duration.ofHours(49));idle();
    assertThat(instance).isCompleted().hasPassedElement("Event_1xmyihl").hasNotPassedElement("Activity_0t8snic");
  }
  @Test void producerCanStartAndSubmitFromTasklist() throws Exception {
    var instance=client.newCreateInstanceCommand().bpmnProcessId("Process_0g8kz9d").latestVersion().send().join();idle();
    complete("f2-prepare-update",Map.of("updateId","UI-test","correctionAttempts",0,"productOptions",java.util.List.of()));
    assertThat(instance).isWaitingAtElements("Task_SubmitStockUpdate");
    complete("io.camunda.zeebe:userTask",Map.of("productId","P1","quantity",10,"availableFrom","2026-11-01","availableUntil","2026-12-31"));
    complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",true));
    complete("f2-save-update",Map.of("quantity",10,"withinSeason",true,"lowStockThreshold",5));
    complete("f2-available",Map.of("available",true));
    assertThat(instance).isCompleted().hasPassedElement("Task_SubmitStockUpdate");
  }
  @Test void invalidUpdateUsesCorrectionTaskWithoutMessagePublication() throws Exception {
    var instance=update();complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",false,"correctionAttempts",1));
    complete("f2-request-correction",Map.of());
    assertThat(instance).isWaitingAtElements("Event_0pab392");
    complete("io.camunda.zeebe:userTask",Map.of("quantity",12,"availableFrom","2026-11-01","availableUntil","2026-12-31"));
    complete("f2-validate-quantity",Map.of());
    complete("f2-validate-season",Map.of("updateValid",true));
    complete("f2-save-update",Map.of("quantity",12,"withinSeason",true,"lowStockThreshold",5));
    complete("f2-available",Map.of("available",true));
    assertThat(instance).isCompleted().hasPassedElement("Event_0pab392");
  }
}

