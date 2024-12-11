package com.example.thymeleaf;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.stream.Stream;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.function.Consumer;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import com.example.thymeleaf.dto.CreateStudentDTO;
import com.example.thymeleaf.DtoValidator;

import static org.junit.jupiter.api.Assertions.assertTrue;
// import static com.example.thymeleaf.CreateStudentDtoTest.validateDto;

@SpringBootTest
public class CreateStudentDtoLargeInputTest {

    private Validator validator;
    private DtoValidator dtoValidator;

    @Autowired
    public CreateStudentDtoLargeInputTest(Validator validator) {
        this.validator = validator;
        this.dtoValidator = new DtoValidator(validator);
    }

    private static final String BIG_INPUT = "A".repeat(1_000_000);
    
    @Test
    void name_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setName(BIG_INPUT).hasErrors());
    }

    @Test
    void email_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setEmail(BIG_INPUT).hasErrors());
    }

    @Test
    void zipCode_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setZipCode(BIG_INPUT).hasErrors());
    }

    @Test
    void street_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setStreet(BIG_INPUT).hasErrors());
    }

    @Test
    void number_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setNumber(BIG_INPUT).hasErrors());
    }

    @Test
    void complement_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setComplement(BIG_INPUT).hasErrors());
    }

    @Test
    void district_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setDistrict(BIG_INPUT).hasErrors());
    }

    @Test
    void city_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setCity(BIG_INPUT).hasErrors());
    }

    @Test
    void state_doesnt_accept_big_input() {
        assertTrue(dtoValidator.start().setState(BIG_INPUT).hasErrors());
    }
}
