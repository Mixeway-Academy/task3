package com.example.thymeleaf.dto;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import javax.validation.Validation;
import javax.validation.Validator;
import javax.validation.ValidatorFactory;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

class CreateStudentDTOTest {

    private static final ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
    private final Validator validator = factory.getValidator();
    private CreateStudentDTO student;

    @BeforeEach
    void setUp() {
        student = new CreateStudentDTO();
        student.setName("Jan Kowalski");
        student.setEmail("jan@example.com");
        student.setBirthday(LocalDate.of(2000, 5, 10));
        student.setZipCode("00-001");
        student.setStreet("Polna");
        student.setNumber("10");
        student.setDistrict("Centrum");
        student.setCity("Warszawa");
        student.setState("Mazowieckie");
    }

    @AfterAll
    static void closeValidatorFactory() {
        factory.close();
    }

    @Test
    void validData() {
        assertTrue(validator.validate(student).isEmpty());
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"   "})
    void invalidName(String name) {
        student.setName(name);
        assertFalse(validator.validateProperty(student, "name").isEmpty());
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"bez-malpy", "jan@"})
    void invalidEmail(String email) {
        student.setEmail(email);
        assertFalse(validator.validateProperty(student, "email").isEmpty());
    }

    @Test
    void missingBirthday() {
        student.setBirthday(null);
        assertFalse(validator.validateProperty(student, "birthday").isEmpty());
    }

    @Test
    void futureBirthday() {
        student.setBirthday(LocalDate.now().plusDays(1));
        assertFalse(validator.validateProperty(student, "birthday").isEmpty());
    }

    @Test
    void sqlInjectionAttempt() {
        student.setName("Robert'); DROP TABLE student; --");
        assertFalse(validator.validateProperty(student, "name").isEmpty());
    }

    @Test
    void javaScriptInjectionAttempt() {
        student.setName("<script>alert('XSS')</script>");
        assertFalse(validator.validateProperty(student, "name").isEmpty());
    }

    @Test
    void veryLongName() {
        student.setName("a".repeat(10000));
        assertFalse(validator.validateProperty(student, "name").isEmpty());
    }

    @Test
    void veryOldBirthday() {
        student.setBirthday(LocalDate.of(1, 1, 1));
        assertFalse(validator.validateProperty(student, "birthday").isEmpty());
    }
}
