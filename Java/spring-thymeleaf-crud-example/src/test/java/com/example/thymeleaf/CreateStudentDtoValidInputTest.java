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
public class CreateStudentDtoValidInputTest {

    private final Validator validator;
    private final DtoValidator dtoValidator;

    @Autowired
    public CreateStudentDtoValidInputTest(Validator validator) {
        this.dtoValidator = new DtoValidator(validator);
        this.validator = validator;
    }
    
    @ParameterizedTest
    @ValueSource(strings = {
        "Thomas Anderson",
        "Robert F. Kennedy Jr.",
        "Thomas Alva Edison",
        "京房",
        "東方",
        "Günter Hermann"
    })
    void name_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setName(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "me@example.com",
        "thomas.anderson@metacortex.com",
        "name+tag@example.com",
        "\"spaces may be quoted\"@example.com"
    })
    void email_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setEmail(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "00-621",
        "21384-200"
    })
    void zip_code_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setZipCode(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "al. Jerzego Waszyngtona",
        "ul. Polna",
        "257th Ave"
    })
    void street_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setStreet(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "21",
        "42B"
    })
    void number_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setNumber(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "Apartment 21",
        "Floor 10",
        "Next to the gas station"
    })
    void complement_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setComplement(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "Włochy",
        "Brooklyn",
        "Manhattan",
        "Friedrichshain-Kreuzberg"
    })
    void district_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setDistrict(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "Berlin",
        "Warsaw",
        "New York",
        "臺北"
    })
    void city_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setCity(input).hasErrors());
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "New York",
        "Providence",
        "California",
        "Mazowieckie"
    })
    void state_accepts_valid_input(String input) {
        assertFalse(dtoValidator.start().setState(input).hasErrors());
    }
}
