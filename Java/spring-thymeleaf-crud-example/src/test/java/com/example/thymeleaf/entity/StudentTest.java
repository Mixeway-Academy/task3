package com.example.thymeleaf.entity;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.regex.Pattern;

class StudentTest {

    // Testy poprawnych danych
    @Test
    void testValidData() {
        Student student = new Student();

        student.setId("123");
        student.setName("John Doe");
        student.setEmail("john.doe@example.com");
        student.setBirthday(LocalDate.of(1990, 1, 1));

        assertEquals("123", student.getId(), "ID should be set correctly");
        assertEquals("John Doe", student.getName(), "Name should be set correctly");
        assertEquals("john.doe@example.com", student.getEmail(), "Email should be set correctly");
        assertEquals(LocalDate.of(1990, 1, 1), student.getBirthday(), "Birthday should be set correctly");
    }

    // Testy niepoprawnych danych
    @Test
    void testInvalidData() {
        Student student = new Student();

        student.setName(null);
        student.setEmail("not-an-email");
        student.setBirthday(LocalDate.of(3000, 1, 1)); // Futuristic date (assuming no validation)

        assertNotNull(student.getName(), "Name shouldn't allow null values");
        assertNotEquals("not-an-email", student.getEmail(), "Invalid email shouldn't be allowed");
        assertEquals(LocalDate.of(3000, 1, 1), student.getBirthday(), "Birthday shouldn't store invalid dates");
    }

    // Testy związane z próbą wstrzyknięcia kodu SQL
    @Test
    void testSqlInjectionAttempt() {
        Student student = new Student();

        String maliciousInput = "John'; DROP TABLE students; --";
        student.setName(maliciousInput);

        assertNotEquals(maliciousInput, student.getName(), "Name shouldn't store malicious SQL input");
    }

    // Testy związane z próbą wstrzyknięcia kodu JavaScript
    @Test
    void testJavaScriptInjectionAttempt() {
        Student student = new Student();

        String maliciousInput = "<script>alert('Hacked!')</script>";
        student.setName(maliciousInput);

        assertNotEquals(maliciousInput, student.getName(), "Name shouldn't store malicious JavaScript");
    }

    // Testy ekstremalne
    @Test
    void testExtremeData() {
        Student student = new Student();

        String longName = "a".repeat(10000); // Very long name
        student.setName(longName);

        assertNotEquals(longName, student.getName(), "Name should store extremely long strings");

        String specialChars = "!@#$%^&*()_+{}|:\"<>?~`";
        student.setName(specialChars);

        assertNotEquals(specialChars, student.getName(), "Name shouldn't store special characters correctly");
    }
    @Test
    void testStudentSettersAndGetters() {
        Student student = new Student();

        // Setting values
        student.setId("123");
        student.setName("John Doe");
        student.setEmail("john.doe@example.com");
        student.setBirthday(LocalDate.of(1990, 1, 1));
        student.setCreatedAt(LocalDateTime.of(2023, 1, 1, 12, 0));
        student.setUpdatedAt(LocalDateTime.of(2023, 2, 1, 12, 0));

        // Verifying values
        assertEquals("123", student.getId());
        assertEquals("John Doe", student.getName());
        assertEquals("john.doe@example.com", student.getEmail());
        assertEquals(LocalDate.of(1990, 1, 1), student.getBirthday());
        assertEquals(LocalDateTime.of(2023, 1, 1, 12, 0), student.getCreatedAt());
        assertEquals(LocalDateTime.of(2023, 2, 1, 12, 0), student.getUpdatedAt());
    }

    @Test
    void testDefaultValues() {
        Student student = new Student();

        // Default values should be null
        assertNull(student.getId(), "ID should be null by default");
        assertNull(student.getName(), "Name should be null by default");
        assertNull(student.getEmail(), "Email should be null by default");
        assertNull(student.getBirthday(), "Birthday should be null by default");
        assertNull(student.getCreatedAt(), "CreatedAt should be null by default");
        assertNull(student.getUpdatedAt(), "UpdatedAt should be null by default");
    }
}
