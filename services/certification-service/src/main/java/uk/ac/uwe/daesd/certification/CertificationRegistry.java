package uk.ac.uwe.daesd.certification;

import java.util.regex.Pattern;

/**
 * Decides the answer for a certification reference. It stands in for a real UK organic control body,
 * so each answer can be triggered on demand in a demo (docs/camunda-variables.md, section 5).
 *
 * <ul>
 *   <li>{@code GB-ORG-00}: the service is unavailable (no reply)</li>
 *   <li>{@code GB-ORG-99}: the certificate is rejected</li>
 *   <li>any other {@code GB-ORG-nn}: the certificate is verified</li>
 *   <li>anything else (missing or wrong format): rejected</li>
 * </ul>
 */
public class CertificationRegistry {

  static final String UNAVAILABLE_REFERENCE = "GB-ORG-00";
  static final String REJECTED_REFERENCE = "GB-ORG-99";
  private static final Pattern UK_ORGANIC_CODE = Pattern.compile("GB-ORG-\\d{2}");

  public CertificationResult check(String certificationReference) {
    if (certificationReference == null) {
      return CertificationResult.REJECTED;
    }
    String reference = certificationReference.trim().toUpperCase();
    if (!UK_ORGANIC_CODE.matcher(reference).matches()) {
      return CertificationResult.REJECTED;
    }
    if (reference.equals(UNAVAILABLE_REFERENCE)) {
      return CertificationResult.UNAVAILABLE;
    }
    if (reference.equals(REJECTED_REFERENCE)) {
      return CertificationResult.REJECTED;
    }
    return CertificationResult.VERIFIED;
  }
}
