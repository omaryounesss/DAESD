package uk.ac.uwe.daesd.certification;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** Unit tests: which answer each certification reference gets. */
class CertificationRegistryTest {

  private final CertificationRegistry registry = new CertificationRegistry();

  @Test
  void demoReferenceGbOrg05IsVerified() {
    assertThat(registry.check("GB-ORG-05")).isEqualTo(CertificationResult.VERIFIED);
  }

  @Test
  void demoReferenceGbOrg99IsRejected() {
    assertThat(registry.check("GB-ORG-99")).isEqualTo(CertificationResult.REJECTED);
  }

  @Test
  void demoReferenceGbOrg00SimulatesAnOutage() {
    assertThat(registry.check("GB-ORG-00")).isEqualTo(CertificationResult.UNAVAILABLE);
  }

  @ParameterizedTest
  @ValueSource(strings = {"GB-ORG-02", "GB-ORG-13", " gb-org-07 "})
  void otherUkOrganicCodesAreVerified(String reference) {
    assertThat(registry.check(reference)).isEqualTo(CertificationResult.VERIFIED);
  }

  @ParameterizedTest
  @ValueSource(strings = {"", "SOIL-123", "GB-ORG-5", "GB-ORG-123", "FR-BIO-01"})
  void malformedReferencesAreRejected(String reference) {
    assertThat(registry.check(reference)).isEqualTo(CertificationResult.REJECTED);
  }

  @Test
  void missingReferenceIsRejected() {
    assertThat(registry.check(null)).isEqualTo(CertificationResult.REJECTED);
  }

  @Test
  void rejectedAndVerifiedCarryTheMessageValueTheProcessExpects() {
    assertThat(CertificationResult.VERIFIED.messageValue()).isEqualTo("verified");
    assertThat(CertificationResult.REJECTED.messageValue()).isEqualTo("rejected");
    assertThat(CertificationResult.UNAVAILABLE.messageValue()).isNull();
  }
}
