package uk.ac.uwe.daesd;
import io.camunda.zeebe.model.bpmn.Bpmn;
import java.nio.file.*;
import org.junit.jupiter.api.Test;
class ModelValidationTest {
  @Test void validateActualExecutableBpmn() throws Exception {
    for (var functionality : new String[]{"f1", "f2"}) {
    try(var files=Files.list(Path.of("..","..","camunda",functionality,"processes"))) {
      for(var file:files.toList()) Bpmn.validateModel(Bpmn.readModelFromFile(file.toFile()));
    }
    }
  }
}

