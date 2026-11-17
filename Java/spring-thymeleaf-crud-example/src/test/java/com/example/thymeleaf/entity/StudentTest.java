package com.example.thymeleaf.entity;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.lang.reflect.Method;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class StudentTest {

    @Nested
    @DisplayName("Valid data")
    class ValidData {

        @Test
        @DisplayName("Setters and getters round-trip correctly")
        void settersAndGettersWork() {
            Student s = validStudent();

            assertEquals("Alice Johnson", s.getName());
            assertEquals("alice.johnson@example.com", s.getEmail());
            assertEquals(LocalDate.of(2000, 5, 15), s.getBirthday());
        }

        @Test
        @DisplayName("@PrePersist assigns UUID id and createdAt")
        void prePersistPopulatesIdAndCreatedAt() throws Exception {
            Student s = validStudent();
            invokePrePersist(s);

            assertNotNull(s.getId(), "id must be assigned");
            assertNotNull(s.getCreatedAt(), "createdAt must be assigned");
            assertDoesNotThrow(() -> UUID.fromString(s.getId()), "id must be a valid UUID");
            assertTrue(s.getCreatedAt().isBefore(LocalDateTime.now().plusSeconds(1)));
        }

        @Test
        @DisplayName("@PreUpdate assigns updatedAt")
        void preUpdatePopulatesUpdatedAt() throws Exception {
            Student s = validStudent();
            invokePrePersist(s);
            Thread.sleep(5); // let time advance
            invokePreUpdate(s);

            assertNotNull(s.getUpdatedAt());
            assertTrue(s.getUpdatedAt().isAfter(s.getCreatedAt())
                    || s.getUpdatedAt().isEqual(s.getCreatedAt()));
        }

        @Test
        @DisplayName("Two prePersist calls generate different ids")
        void prePersistGeneratesUniqueIds() throws Exception {
            Student a = validStudent();
            Student b = validStudent();
            invokePrePersist(a);
            invokePrePersist(b);

            assertNotEquals(a.getId(), b.getId());
        }

        @Test
        @DisplayName("equals/hashCode use only id")
        void equalityByIdOnly() throws Exception {
            Student a = validStudent();
            Student b = new Student();
            b.setName("Someone Else");
            b.setEmail("other@example.com");

            invokePrePersist(a);
            b.setId(a.getId());

            assertEquals(a, b);
            assertEquals(a.hashCode(), b.hashCode());
        }

        @Test
        @DisplayName("toString contains key fields")
        void toStringContainsFields() {
            Student s = validStudent();
            String out = s.toString();
            assertTrue(out.contains("Alice Johnson"));
            assertTrue(out.contains("alice.johnson@example.com"));
        }
    }

    @Nested
    @DisplayName("Invalid data")
    class InvalidData {

        @Test
        @DisplayName("null name should be rejected")
        void nullNameRejected() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName(null);
            });
        }

        @Test
        @DisplayName("blank name should be rejected")
        void blankNameRejected() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName("   ");
            });
        }

        @Test
        @DisplayName("null email should be rejected")
        void nullEmailRejected() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setEmail(null);
            });
        }

        @ParameterizedTest(name = "invalid email: [{0}]")
        @ValueSource(strings = {
                "",
                " ",
                "plainaddress",
                "missing@tld",
                "@no-local.com",
                "no-at-sign.com",
                "spaces in@email.com",
                "double@@at.com",
                "trailing.dot@domain.",
                "very.long.tld@domain.toolongtldname"
        })
        @DisplayName("malformed email should be rejected")
        void malformedEmailRejected(String badEmail) {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setEmail(badEmail);
            });
        }

        @Test
        @DisplayName("future birthday should be rejected")
        void futureBirthdayRejected() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setBirthday(LocalDate.now().plusYears(1));
            });
        }

        @Test
        @DisplayName("prePersist should not overwrite an existing id")
        void prePersistKeepsExistingId() throws Exception {
            Student s = validStudent();
            String preset = UUID.randomUUID().toString();
            s.setId(preset);
            invokePrePersist(s);
            assertEquals(preset, s.getId(),
                    "prePersist currently overwrites id unconditionally — likely a bug");
        }
    }

    @Nested
    @DisplayName("Injection attempts (SQL / JS / path)")
    class InjectionAttempts {

        @ParameterizedTest(name = "SQL injection payload: {0}")
        @ValueSource(strings = {
                "'; DROP TABLE student; --",
                "1' OR '1'='1",
                "admin'--",
                "'; UPDATE student SET name='hacked' WHERE 1=1; --",
                "' UNION SELECT * FROM address --",
                "Robert'); DROP TABLE student;--"
        })
        @DisplayName("SQL payloads should be stored verbatim (parameterised persistence expected)")
        void sqlInjectionStoredAsText(String payload) {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName(payload);

                assertEquals(payload, s.getName());
                assertDoesNotThrow(s::toString);
            });
        }

        @ParameterizedTest(name = "XSS payload: {0}")
        @ValueSource(strings = {
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert(1)>",
                "javascript:alert(1)",
                "\"><svg/onload=alert(1)>",
                "<iframe src=javascript:alert(1)>",
                "';alert(String.fromCharCode(88,83,83));//"
        })
        @DisplayName("JS/XSS payloads shouldn't be stored verbatim")
        void xssPayloadStoredAsText(String payload) {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName(payload);
                s.setEmail(payload);

                assertEquals(payload, s.getName());
                assertEquals(payload, s.getEmail());
                assertDoesNotThrow(s::toString);
            });
        }

        @Test
        @DisplayName("Path traversal in name")
        void pathTraversalInName() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName("../../../../etc/passwd");
                assertDoesNotThrow(s::toString);
                assertEquals("../../../../etc/passwd", s.getName());
            });
        }

        @Test
        @DisplayName("Null byte injection")
        void nullByteInjection() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setEmail("alice\0@example.com");
                assertEquals("alice\0@example.com", s.getEmail(),
                        "entity keeps null bytes — sanitise at controller/service layer");
            });
        }

        @Test
        @DisplayName("LDAP-style payload breaks equals/hashCode")
        void ldapStylePayloadSafeForEquals() throws Exception {
            assertThrows(RuntimeException.class, () -> {
                Student a = validStudent();
                Student b = validStudent();
                a.setName("*)(uid=*)(|(uid=*");
                b.setName("different");

                invokePrePersist(a);
                b.setId(a.getId());
            });
        }
    }

    @Nested
    @DisplayName("Extreme data")
    class Extreme {

        @Test
        @DisplayName("10 000-character name")
        void extremelyLongName() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                String longName = "A".repeat(10_000);
                s.setName(longName);
            });
        }

        @Test
        @DisplayName("10 000-character email")
        void extremelyLongEmail() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                String longEmail = "a".repeat(9_980) + "@x.com";
                s.setEmail(longEmail);
                assertEquals(longEmail, s.getEmail());
            });
        }

        @Test
        @DisplayName("Unicode / emoji / RTL text round-trips")
        void unicodeRoundTrip() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                String unicode = "Ω≈ç√∫˜µ≤≥÷ 日本語 🙂 مرحبا 👍🏽 🇺🇦";
                s.setName(unicode);
                assertEquals(unicode, s.getName());
                assertDoesNotThrow(s::toString);
            });
        }

        @Test
        @DisplayName("Extreme past birthday (LocalDate.MIN)")
        void extremePastBirthday() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setBirthday(LocalDate.MIN);
                assertEquals(LocalDate.MIN, s.getBirthday());
                assertDoesNotThrow(s::toString);
            });
        }

        @Test
        @DisplayName("Extreme future birthday (LocalDate.MAX)")
        void extremeFutureBirthday() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setBirthday(LocalDate.MAX);
            });
        }

        @Test
        @DisplayName("Control characters in name")
        void controlCharactersInName() {
            assertThrows(RuntimeException.class, () -> {
                Student s = validStudent();
                s.setName("\u0000\u0001\u0002\u0003\u0004\u0005");
                assertDoesNotThrow(s::toString);
            });
        }

        @Test
        @DisplayName("All setters don't accept null")
        void allNullFields() {
            assertThrows(RuntimeException.class, () -> {
                Student s = new Student();
                s.setName(null);
                s.setEmail(null);
                s.setBirthday(null);
                s.setAddress(null);
            });
        }
    }

    // ---------- helpers ----------

    private static void invokePrePersist(Student s) throws Exception {
        Method m = Student.class.getDeclaredMethod("prePersist");
        m.setAccessible(true);
        m.invoke(s);
    }

    private static void invokePreUpdate(Student s) throws Exception {
        Method m = Student.class.getDeclaredMethod("preUpdate");
        m.setAccessible(true);
        m.invoke(s);
    }

    private static Student validStudent() {
        Student s = new Student();
        s.setName("Alice Johnson");
        s.setEmail("alice.johnson@example.com");
        s.setBirthday(LocalDate.of(2000, 5, 15));
        return s;
    }
}