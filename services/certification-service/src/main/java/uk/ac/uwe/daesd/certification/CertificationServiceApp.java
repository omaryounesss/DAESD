package uk.ac.uwe.daesd.certification;

import io.camunda.zeebe.client.ZeebeClient;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Starts the simulated organic-certification service as a Camunda 8 job worker.
 *
 * <p>Local Camunda 8 Run (default): connects to localhost:26500 with no credentials.
 * Camunda 8 SaaS: set CAMUNDA_CLUSTER_ID, CAMUNDA_CLUSTER_REGION, ZEEBE_CLIENT_ID and
 * ZEEBE_CLIENT_SECRET (from the cluster's API client).
 */
public class CertificationServiceApp {

  private static final Logger LOG = LoggerFactory.getLogger(CertificationServiceApp.class);

  public static void main(String[] args) throws InterruptedException {
    Duration replyDelay = Duration.ofSeconds(Long.parseLong(env("REPLY_DELAY_SECONDS", "2")));

    try (ZeebeClient client = buildClient()) {
      var handler = new CertificationJobHandler(client, new CertificationRegistry(), replyDelay);
      var worker = client.newWorker()
          .jobType(CertificationJobHandler.JOB_TYPE)
          .handler(handler)
          .fetchVariables("listingId", "certificationReference", "producerName")
          .name("simulated-certification-service")
          .open();

      LOG.info("Certification service running. Waiting for '{}' jobs. Press Ctrl+C to stop.",
          CertificationJobHandler.JOB_TYPE);

      CountDownLatch stop = new CountDownLatch(1);
      Runtime.getRuntime().addShutdownHook(new Thread(() -> {
        worker.close();
        handler.shutdown();
        stop.countDown();
      }));
      stop.await();
    }
  }

  private static ZeebeClient buildClient() {
    String clusterId = System.getenv("CAMUNDA_CLUSTER_ID");
    if (clusterId != null && !clusterId.isBlank()) {
      LOG.info("Connecting to Camunda 8 SaaS cluster {}", clusterId);
      return ZeebeClient.newCloudClientBuilder()
          .withClusterId(clusterId)
          .withClientId(System.getenv("ZEEBE_CLIENT_ID"))
          .withClientSecret(System.getenv("ZEEBE_CLIENT_SECRET"))
          .withRegion(env("CAMUNDA_CLUSTER_REGION", "bru-2"))
          .build();
    }
    String address = env("ZEEBE_ADDRESS", "localhost:26500");
    LOG.info("Connecting to local Camunda at {}", address);
    return ZeebeClient.newClientBuilder().gatewayAddress(address).usePlaintext().build();
  }

  private static String env(String name, String fallback) {
    String value = System.getenv(name);
    return value == null || value.isBlank() ? fallback : value;
  }
}
