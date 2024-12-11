package com.example.thymeleaf;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.stream.Stream;
import java.util.Arrays;
import java.util.ArrayList;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import com.example.thymeleaf.dto.CreateStudentDTO;
import com.example.thymeleaf.DtoValidator;

import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
class CreateStudentDtoSqliTest {

    private Validator validator;
    private DtoValidator dtoValidator;

    @Autowired
    public CreateStudentDtoSqliTest(Validator validator) {
        this.validator = validator;
        this.dtoValidator = new DtoValidator(validator);
    }

    private static final String[] SQLI_INPUT = {
        "' or 0=0 #",
        "or true--",
        "\" or \"\"*\"",
        "' or 1=1–",
        "admin' and substring(password/text(),1,1)='7",
        "' or '1'='1",
        "admin') or '1'='1'--",
        "' UNION ALL SELECT system_user(),user();#",
        "' or 'one'='one",
        "' or ''^'",
        "\" or 1=1 --",
        "admin\" or 1=1#",
        "\"*\"",
        "'or'1=1",
        "\" or 0=0 #",
        "admin\" or \"1\"=\"1\"#",
        "%' or '0'='0",
        " or true",
        "or 1=1#",
        "' or '1'='1'--",
        "admin\") or \"1\"=\"1\"/*",
        "') or ('1'='1'--",
        "'/*",
        "\" or \"\"&\"",
        "\"-\"",
        ") or ('1′='1–",
        "' or '1'='1'/*",
        "admin') or '1'='1",
        "'=\"or'",
        " or 0=0 --",
        "\") or \"1\"=\"1\"--",
        "\") or \"1\"=\"1\"/*",
        "' AND 1=0 UNION ALL SELECT '', '81dc9bdb52d04dc20036dbd8313ed055",
        "\" #",
        "admin'or 1=1 or ''='",
        "' or '1'='1'#",
        "' UNION ALL SELECT 1, @@version;#",
        "\" or 1=1–",
        "' or 1=1 –",
        "' or '1′='1",
        "admin') or ('1'='1'--",
        "' OR 'x'='x'#;",
        "\" or 1=1--",
        "\") or true--",
        "' or username like '%",
        "admin' or '1'='1'#",
        "\"^\"",
        "\") or \"1\"=\"1\"#",
        "admin\" #",
        "'or'1=1′",
    };

    private static final String[] getSqliInput() {
        return SQLI_INPUT;
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void name_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setName(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void email_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setEmail(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void zipCode_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setZipCode(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void streetName_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setStreet(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void buildingNumber_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setNumber(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void addressComplement_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setComplement(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void district_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setDistrict(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void city_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setCity(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getSqliInput")
    void state_doesnt_accept_sqli(String input) {
        assertTrue(dtoValidator.start().setState(input).hasErrors());
    }
}
