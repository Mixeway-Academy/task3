package com.example.thymeleaf;

import static javax.validation.Validation.buildDefaultValidatorFactory;
import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.Set;
import javax.validation.*;

import com.example.thymeleaf.dto.CreateStudentDTO;

public class StudentTests {

    private Validator validator;

    @BeforeEach
    void setup() {
        ValidatorFactory factory = buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    // testy poprawnych danych

    @Test
    void testSafeInput() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika");
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertTrue(violations.isEmpty());
    }

    // testy niepoprawnych danych

    @Test
    void testIncorrectInput_Null() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName(null);
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertTrue(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_MissingFields() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_EmptyFields() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("");
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_WrongEmailFormat() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setEmail("wrong-email");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_BoundaryEmailFormat() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika");
        dto.setEmail("wrong.@email.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_BoundaryEmailLength() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika");
        dto.setEmail("x".repeat(64) + "@email.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInput_FutureBirthday() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika");
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.now().plusDays(1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    // testy JavaScript injection

    @Test
    void testUnsafeInput_XSSInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("><img src=x onerror=\"alert(' hacking ')\"><a hre=\"a");
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Main Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        System.out.println(violations);

        assertFalse(violations.isEmpty());
    }

    @Test
    void testUnsafeInput_XSSInNumber() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("monika");
        dto.setEmail("abc@example.com");
        dto.setStreet("Street");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setNumber("javascript:alert('xss')");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertFalse(violations.isEmpty());
    }

    // testy SQL injection

    @Test
    void testUnsafeInput_SQLInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika'); DROP TABLE student; --");
        dto.setEmail("abc@example.com");
        dto.setStreet("Street");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertFalse(violations.isEmpty());
    }

    @Test
    void testUnsafeInput_SQLInNumber() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Monika");
        dto.setEmail("abc@example.com");
        dto.setStreet("Street");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setNumber("1' ORDER BY 1--+");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertFalse(violations.isEmpty());
    }

    // testy ekstremalne

    @Test
    void testExtremeInput_MaxLengthInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("x".repeat(300));
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("10");
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testExtremeInput_MaxNumber() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("x".repeat(300));
        dto.setEmail("abc@example.com");
        dto.setBirthday(LocalDate.of(2000, 1, 1));
        dto.setZipCode("00-001");
        dto.setStreet("Street");
        dto.setNumber("1" + "0".repeat(10));
        dto.setDistrict("District");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

}
