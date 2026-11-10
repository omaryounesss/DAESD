package uk.ac.uwe.daesd.certification;

/** The three answers the simulated certification service can give. */
public enum CertificationResult {
  /** The certificate is valid: the process publishes the product as organic. */
  VERIFIED("verified"),
  /** The certificate is not valid: the producer must remove the claim or withhold the listing. */
  REJECTED("rejected"),
  /** The service is "down": it sends no reply, so the process times out and retries. */
  UNAVAILABLE(null);

  private final String messageValue;

  CertificationResult(String messageValue) {
    this.messageValue = messageValue;
  }

  /** Value of {@code certificationStatus} in the reply message, or {@code null} when no reply is sent. */
  public String messageValue() {
    return messageValue;
  }
}
