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
class CreateStudentDtoXssTest {

    private Validator validator;
    private DtoValidator dtoValidator;

    @Autowired
    public CreateStudentDtoXssTest(Validator validator) {
        this.validator = validator;
        this.dtoValidator = new DtoValidator(validator);
    }
    
    private static final String[] XSS_INPUT = {
        "';a=prompt,a()//",
        "'-eval(\"window['pro'%2B'mpt'](8)\")-'",
        "<image/src/onerror=prompt(8)>",
        "<svg onload=alert(1)>",
        "</script><svg onload=alert(1)>",
        "<rb onblur=alert(1) tabindex=1 id=x></rb><input autofocus>",
        "<dt onfocusout=alert(1) tabindex=1 id=x></dt><input autofocus>",
        "<div id=\"42\"><head><base href=\"javascript://\"/></head><body><a href=\"/. /,alert(42)//#\">XXX</a></body>//[\"'`-->]]>]</div>",
        "<style>@keyframes x{}</style><header style=\"animation-name:x\" onanimationstart=\"alert(1)\"></header>",
        "<nextid onmouseover=\"alert(1)\">test</nextid>",
        "<shadow onkeypress=\"alert(1)\" contenteditable>test</shadow>",
        "<tr onbeforepaste=\"alert(1)\" contenteditable>test</tr>",
        "<header onmousemove=\"alert(1)\">test</header>",
        "<nextid onmousemove=\"alert(1)\">test</nextid>",
        "<template onblur=alert(1) tabindex=1 id=x></template><input autofocus>",
        "<div draggable=\"true\" contenteditable>drag me</div><menu ondrop=alert(1) contenteditable>drop here</menu>",
        "<x contenteditable onkeyup=alert(1)>press any key! ",
        "<cite onkeyup=\"alert(1)\" contenteditable>test</cite>",
        "<area onclick=\"alert(1)\">test</area>",
        "<div draggable=\"true\" contenteditable>drag me</div><noscript ondragover=alert(1) contenteditable>drop here</noscript>",
        "<rp onmouseleave=\"alert(1)\">test</rp>",
        "<h1 id=x tabindex=1 onactivate=alert(1)></h1>",
        "<style>:target {color: red;}</style><area id=x style=\"transition:color 10s\" ontransitioncancel=alert(1)></area>",
        "<input onauxclick=alert(1)>",
        "<style>:target {color:red;}</style><area id=x style=\"transition:color 1s\" ontransitionend=alert(1)></area>",
    };

    private static final String[] getXssInput() {
        return XSS_INPUT;
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void name_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setName(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void email_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setEmail(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void zipCode_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setZipCode(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void streetName_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setStreet(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void buildingNumber_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setNumber(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void addressComplement_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setComplement(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void district_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setDistrict(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void city_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setCity(input).hasErrors());
    }

    @ParameterizedTest
    @MethodSource("getXssInput")
    void state_doesnt_accept_xss(String input) {
        assertTrue(dtoValidator.start().setState(input).hasErrors());
    }
}
