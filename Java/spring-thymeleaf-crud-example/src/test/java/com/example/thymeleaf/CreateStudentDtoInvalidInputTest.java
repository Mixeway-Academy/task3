package com.example.thymeleaf;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.ValueSource;
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
import static org.junit.jupiter.api.Assertions.assertFalse;

@SpringBootTest
public class CreateStudentDtoInvalidInputTest {

    private final Validator validator;
    private final DtoValidator dtoValidator;

    @Autowired
    public CreateStudentDtoInvalidInputTest(Validator validator) {
        this.dtoValidator = new DtoValidator(validator);
        this.validator = validator;
    }

    private static final String[] INVALID_INPUT = {
        "",
        null,
        " ",
        "\t",
        "\n",
        "0",
        "null",
        "[object Object]"
    };
    
    private static final String[] getInvalidinput() {
        return INVALID_INPUT;
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    @ValueSource(strings = {
        "awevaev29aijeoiva9",
        "     \t\t \n",
        "!@@#!%!%(^*! []!%!%"
    })
    void name_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setName(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    @ValueSource(strings = {
        "me @ example.com",
        "  @example.com",
        "--",
        "@()!5701852@ex0815.com",
    })
    void email_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setEmail(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    @ValueSource(strings = {
        "aoiva",
        "21-adsf",
        "asdf-39",
        "0158025"
    })
    void zip_code_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setZipCode(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    @ValueSource(strings = {
        "[avadsf]va"
    })
    void street_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setStreet(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    @ValueSource(strings = {
        "AJGO",
        "@!%!^9"
    })
    void number_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setNumber(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    void complement_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setComplement(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    void district_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setDistrict(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    void city_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setCity(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getInvalidinput")
    void state_doesnt_accept_invalid_input(String input) {
        assertTrue(dtoValidator.start().setState(input).hasErrors());
    }
}
