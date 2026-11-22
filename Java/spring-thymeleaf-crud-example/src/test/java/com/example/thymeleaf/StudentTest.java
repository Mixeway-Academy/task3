package com.example.thymeleaf;

import static javax.validation.Validation.buildDefaultValidatorFactory;
import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.Set;
import javax.validation.*;

import com.example.thymeleaf.dto.CreateStudentDTO;

public class StudentTest {

    private Validator validator;

    @BeforeEach
    void setup() {
        ValidatorFactory factory = buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    void testCorrectInput() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertTrue(violations.isEmpty());
    }

    // Incorrect data
    @Test
    void testIncorrectInputNNull() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName(null);
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertTrue(violations.isEmpty());
    }

    @Test
    void testIncorrectInputMissingFields() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInputEmptyFields() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInputWrongEmailFormat() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setEmail("the-email");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInputBoundaryEmailFormat() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej");
        dto.setEmail("wrong.@email.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInputBoundaryEmailLength() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej");
        dto.setEmail("x".repeat(64) + "@email.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testIncorrectInputFutureBirthday() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.now().plusDays(1));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    // Testy Injection

    @Test
    void testUnsafeInputXSSInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("><img src=x onerror=\"alert(' hacking ')\"><a hre=\"a");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("3");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        System.out.println(violations);

        assertFalse(violations.isEmpty());
    }

    @Test
    void testUnsafeInputXSSInNumber() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("javascript:alert('xss')");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertFalse(violations.isEmpty());
    }

    // testy SQL injection

    @Test
    void testUnsafeInput_SQLInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("Bartlomiej'); DROP TABLE student; --");
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("7");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");
        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);

        assertFalse(violations.isEmpty());
    }

    // Testy ekstremalne

    @Test
    void testMaxInputLengthInName() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("x".repeat(300));
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("7");
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

    @Test
    void testMaxInputNumber() {
        CreateStudentDTO dto = new CreateStudentDTO();
        dto.setName("x".repeat(300));
        dto.setEmail("mariaan_cv@gmail.com");
        dto.setBirthday(LocalDate.of(2002, 3, 11));
        dto.setZipCode("00-010");
        dto.setStreet("Street");
        dto.setNumber("1" + "0".repeat(10));
        dto.setDistrict("Ohio");
        dto.setCity("Warszawa");
        dto.setState("Mazowieckie");

        Set<ConstraintViolation<CreateStudentDTO>> violations = validator.validate(dto);
        assertFalse(violations.isEmpty());
    }

}