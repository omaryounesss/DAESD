package uk.ac.uwe.daesd.certification;

import io.camunda.zeebe.client.ZeebeClient;
import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.client.api.worker.JobClient;
import io.camunda.zeebe.client.api.worker.JobHandler;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Handles the service task "Request certification verification" in F1.
 *
 * <ol>
 *   <li>Takes the job and reads listingId, certificationReference and producerName.</li>
 *   <li>Completes the job straight away (the request has been received).</li>
 *   <li>Later, replies with message {@code certification-result}, correlated by listingId,
 *       carrying {@code certificationStatus = "verified" | "rejected"}. When the service is
 *       "unavailable" it sends no reply, and the process's 30-second timer takes over.</li>
 * </ol>
 */
public class CertificationJobHandler implements JobHandler {

  public static final String JOB_TYPE = "request-certification-verification";
  public static final String REPLY_MESSAGE = "certification-result";

  private static final Logger LOG = LoggerFactory.getLogger(CertificationJobHandler.class);

  private final ZeebeClient client;
  private final CertificationRegistry registry;
  private final Duration replyDelay;
  private final ScheduledExecutorService replies = Executors.newSingleThreadScheduledExecutor(r -> {
    Thread thread = new Thread(r, "certification-replies");
    thread.setDaemon(true);
    return thread;
  });

  /**
   * @param replyDelay how long the "external service" takes to answer. Zero replies immediately
   *     (used in tests); a couple of seconds makes the demo look like a real outside service.
   */
  public CertificationJobHandler(ZeebeClient client, CertificationRegistry registry, Duration replyDelay) {
    this.client = client;
    this.registry = registry;
    this.replyDelay = replyDelay;
  }

  @Override
  public void handle(JobClient jobClient, ActivatedJob job) {
    Map<String, Object> variables = job.getVariablesAsMap();
    String listingId = (String) variables.get("listingId");
    String reference = (String) variables.get("certificationReference");
    String producer = (String) variables.get("producerName");

    CertificationResult result = registry.check(reference);
    LOG.info("Request for listing {} from {}: {} -> {}", listingId, producer, reference, result);

    // 1. Acknowledge the request.
    jobClient.newCompleteCommand(job.getKey()).send().join();

    // 2. Reply (or stay silent to simulate an outage).
    if (result == CertificationResult.UNAVAILABLE) {
      LOG.info("Simulating an outage: no reply for listing {}", listingId);
      return;
    }
    if (replyDelay.isZero()) {
      reply(listingId, result);
    } else {
      replies.schedule(() -> reply(listingId, result), replyDelay.toMillis(), TimeUnit.MILLISECONDS);
    }
  }

  private void reply(String listingId, CertificationResult result) {
    client.newPublishMessageCommand()
        .messageName(REPLY_MESSAGE)
        .correlationKey(listingId)
        .variables(Map.of("certificationStatus", result.messageValue()))
        .send()
        .join();
    LOG.info("Replied {} for listing {}", result.messageValue(), listingId);
  }

  /** Stops sending pending replies. */
  public void shutdown() {
    replies.shutdown();
  }
}
