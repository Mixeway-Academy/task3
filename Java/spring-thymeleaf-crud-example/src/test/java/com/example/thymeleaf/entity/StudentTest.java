package com.example.thymeleaf.entity;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;

import java.lang.reflect.Method;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class StudentTest {

    @Test
    @DisplayName("Creates a Student with typical valid values")
    void createsStudentWithValidValues() {
        Student student = assertDoesNotThrow(StudentTest::buildValidStudent);

        assertNotNull(student);
    }

    @Test
    @DisplayName("Generates an identifier and creation time before persistence")
    void assignsGeneratedValuesBeforeInsert() throws Exception {
        Student student = buildValidStudent();

        runCallback(student, "prePersist");

        assertNotNull(student.getId());
        assertDoesNotThrow(() -> UUID.fromString(student.getId()));
        assertNotNull(student.getCreatedAt());
        assertFalse(student.getCreatedAt().isAfter(LocalDateTime.now().plusSeconds(1)));
    }

    @Test
    @DisplayName("Records an update time before an update")
    void recordsTimeBeforeUpdate() throws Exception {
        Student student = buildValidStudent();
        runCallback(student, "prePersist");

        runCallback(student, "preUpdate");

        assertNotNull(student.getUpdatedAt());
        assertFalse(student.getUpdatedAt().isBefore(student.getCreatedAt()));
    }

    @Test
    @DisplayName("Accepts an email with a four-character local part")
    void acceptsEmailWithFourCharacterLocalPart() {
        Student student = buildValidStudent();

        assertDoesNotThrow(() -> student.setEmail("abcd@somecompany.com"));
    }

    @Test
    @DisplayName("Accepts an email with a 64-character local part")
    void acceptsEmailWith64CharacterLocalPart() {
        Student student = buildValidStudent();

        assertDoesNotThrow(() -> student.setEmail("a".repeat(64) + "@somecompany.com"));
    }

    @Test
    @DisplayName("Allows a name at the assumed 255-character limit")
    void acceptsNameAt255Characters() {
        Student student = buildValidStudent();

        assertDoesNotThrow(() -> student.setName("N".repeat(255)));
    }

    @ParameterizedTest
    @ValueSource(strings = {"José", "Łukasz", "李明", "Алексей"})
    @DisplayName("Accepts names with accented and non-Latin letters")
    void acceptsInternationalNames(String name) {
        Student student = buildValidStudent();

        assertDoesNotThrow(() -> student.setName(name));
        assertEquals(name, student.getName());
    }

    @ParameterizedTest
    @ValueSource(strings = {"Alex\u0001Student", "Alex\nStudent", "Alex\tStudent", "Alex\u007fStudent"})
    @DisplayName("Rejects control characters in names")
    void rejectsControlCharactersInName(String name) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(name));
    }

    @ParameterizedTest
    @ValueSource(strings = {"Alex ∑ Student", "Alex √ Student", "Alex = Student"})
    @DisplayName("Rejects mathematical symbols in names")
    void rejectsMathematicalSymbolsInName(String name) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(name));
    }

    @ParameterizedTest
    @NullSource
    @EmptySource
    @ValueSource(strings = {" ", "\t", "\n"})
    @DisplayName("Rejects a missing or blank name")
    void rejectsMissingOrBlankName(String name) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(name));
    }

    @ParameterizedTest
    @NullSource
    @EmptySource
    @ValueSource(strings = {
            "plain-address",
            "no-at-sign.example.com",
            "name@@somecompany.com",
            "name@example.com",
            "name@tld",
            "@somecompany.com",
            "name space@somecompany.com",
            "name@somecompany..com",
            "name@somecompany.com.",
            "name@.somecompany.com"
    })
    @DisplayName("Rejects an email with an invalid format or domain")
    void refusesMalformedEmailAssignment(String email) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setEmail(email));
    }

    @Test
    @DisplayName("Rejects an email with fewer than four local-part characters")
    void rejectsEmailWithShortLocalPart() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setEmail("abc@somecompany.com"));
    }

    @Test
    @DisplayName("Rejects an email with more than 64 local-part characters")
    void rejectsEmailWithLongLocalPart() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class,
                () -> student.setEmail("a".repeat(65) + "@somecompany.com"));
    }

    @Test
    @DisplayName("Rejects an email longer than 77 characters")
    void rejectsEmailLongerThan77Characters() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class,
                () -> student.setEmail("a".repeat(67) + "@somecompany.com"));
    }

    @Test
    @DisplayName("Rejects a birthday after today")
    void refusesFutureBirthday() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class,
                () -> student.setBirthday(LocalDate.now().plusDays(1)));
    }

    @Test
    @DisplayName("Rejects a missing birthday")
    void rejectsMissingBirthday() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setBirthday(null));
    }

    @Test
    @DisplayName("Rejects a missing address")
    void rejectsMissingAddress() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setAddress(null));
    }

    @Test
    @DisplayName("Rejects a name longer than 255 characters")
    void rejectsNameLongerThan255Characters() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName("N".repeat(256)));
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "' OR '1'='1 --",
            "'; DROP TABLE student; --",
            "Robert'); DROP TABLE student;--"
    })
    @DisplayName("Rejects SQL-like input in a name")
    void rejectsSqlLikeName(String payload) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(payload));
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)"
    })
    @DisplayName("Rejects script-like input in a name")
    void rejectsScriptLikeName(String payload) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(payload));
    }

    @ParameterizedTest
    @ValueSource(strings = {"Alex\u0000Student", "\u0000Alex"})
    @DisplayName("Rejects null bytes in names")
    void rejectsNullBytesInName(String name) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(name));
    }

    @ParameterizedTest
    @ValueSource(strings = {"alex\u0000@somecompany.com", "alex@somecompany.com\u0000"})
    @DisplayName("Rejects null bytes in emails")
    void rejectsNullBytesInEmail(String email) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setEmail(email));
    }

    @ParameterizedTest
    @ValueSource(strings = {"../../etc/passwd", "..\\..\\secret.txt"})
    @DisplayName("Rejects path traversal input in names")
    void rejectsTraversalInName(String name) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName(name));
    }

    @ParameterizedTest
    @ValueSource(strings = {"../../secret@somecompany.com", "..\\..\\secret@somecompany.com"})
    @DisplayName("Rejects path traversal input in emails")
    void rejectsTraversalInEmail(String email) {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setEmail(email));
    }

    @Test
    @DisplayName("Rejects a 10-million-character name")
    void rejectsTenMillionCharacterName() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class, () -> student.setName("N".repeat(10_000_000)));
    }

    @Test
    @DisplayName("Rejects an extremely long email")
    void rejectsExtremelyLongEmail() {
        Student student = buildValidStudent();

        assertThrows(IllegalArgumentException.class,
                () -> student.setEmail("a".repeat(10_000) + "@somecompany.com"));
    }

    private static Student buildValidStudent() {
        Address address = new Address();
        address.setZipCode("12345");
        address.setStreet("Main Street");
        address.setNumber("10");
        address.setDistrict("Central");
        address.setCity("Warsaw");
        address.setState("MZ");

        Student student = new Student();
        student.setName("Alex Student");
        student.setEmail("alex@somecompany.com");
        student.setBirthday(LocalDate.of(2000, 1, 1));
        student.setAddress(address);
        address.setStudent(student);
        return student;
    }

    private static void runCallback(Student student, String callbackName) throws Exception {
        Method callback = Student.class.getDeclaredMethod(callbackName);
        callback.setAccessible(true);
        callback.invoke(student);
    }
}
