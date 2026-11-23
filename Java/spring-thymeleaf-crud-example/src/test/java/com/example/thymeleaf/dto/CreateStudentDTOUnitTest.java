package com.example.thymeleaf.dto;

import com.example.thymeleaf.dto.CreateStudentDTO.CreateStudentDTOBuilder;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import javax.validation.ConstraintViolation;
import javax.validation.Validation;
import javax.validation.Validator;
import java.time.LocalDate;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

class CreateStudentDTOUnitTest {

    private static Validator validator;

    @BeforeAll
    static void setUpValidator() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    private static CreateStudentDTOBuilder validStudentBuilder() {
        return CreateStudentDTO.builder()
                .name("Mike Wazowski")
                .email("mike.wazowski@monstersinc.com")
                .birthday(LocalDate.of(1990, 11, 2))
                .zipCode("12-345")
                .street("Scare Floor Avenue")
                .number("7")
                .complement("Apt 2")
                .district("Scare Floor")
                .city("Monstropolis")
                .state("Monster World");
    }

    private static Set<String> invalidFieldsOf(CreateStudentDTO student) {
        return validator.validate(student).stream()
                .map(ConstraintViolation::getPropertyPath)
                .map(Object::toString)
                .collect(Collectors.toSet());
    }

    private static List<String> sqlInjectionPayloads() {
        return List.of(
                "'; DROP TABLE student; --",
                "' OR '1'='1",
                "x' UNION SELECT id, name, email FROM student --"
        );
    }

    private static List<String> xssPayloads() {
        return List.of(
                "<script>alert('XSS wykonany')</script>",
                "<img src=\"https://i.imgur.com/wBIGztj.png\" onload=\"alert('Mike Wazowski')\">",
                "<svg onload=alert(document.cookie)>"
        );
    }

    // ---------- positive tests ----------

    @Test
    void shouldAcceptValidStudent() {
        // given
        CreateStudentDTO student = validStudentBuilder().build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @Test
    void shouldAcceptMissingOptionalComplement() {
        // given
        CreateStudentDTO student = validStudentBuilder().complement(null).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @Test
    void shouldAcceptNonAsciiLetters() {
        // given
        CreateStudentDTO student = validStudentBuilder()
                .name("Mike Ważowski")
                .street("Łąkowa")
                .city("Zürich")
                .build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "mike.wazowski+scare@monstersinc.com",
            "m@w.io",
            "mike_wazowski-1@floor.monstersinc.com"
    })
    void shouldAcceptUnusualButValidEmail(String email) {
        // given
        CreateStudentDTO student = validStudentBuilder().email(email).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @Test
    void shouldAcceptLeapDayBirthday() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.of(2000, 2, 29)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    // ---------- negative tests ----------

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingName(String name) {
        // given
        CreateStudentDTO student = validStudentBuilder().name(name).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("name");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingEmail(String email) {
        // given
        CreateStudentDTO student = validStudentBuilder().email(email).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingZipCode(String zipCode) {
        // given
        CreateStudentDTO student = validStudentBuilder().zipCode(zipCode).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("zipCode");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingStreet(String street) {
        // given
        CreateStudentDTO student = validStudentBuilder().street(street).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("street");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingNumber(String number) {
        // given
        CreateStudentDTO student = validStudentBuilder().number(number).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("number");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingDistrict(String district) {
        // given
        CreateStudentDTO student = validStudentBuilder().district(district).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("district");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingCity(String city) {
        // given
        CreateStudentDTO student = validStudentBuilder().city(city).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("city");
    }

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = "   ")
    void shouldRejectMissingState(String state) {
        // given
        CreateStudentDTO student = validStudentBuilder().state(state).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("state");
    }

    @Test
    void shouldRejectMissingBirthday() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(null).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("birthday");
    }

    @Test
    void shouldReportEveryRequiredFieldForEmptyStudent() {
        // given
        CreateStudentDTO student = CreateStudentDTO.builder().build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields)
                .containsExactlyInAnyOrder("name", "email", "birthday", "zipCode", "street",
                        "number", "district", "city", "state");
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "mike",
            "mike@",
            "@monstersinc.com",
            "mike wazowski@monstersinc.com",
            "mike@@monstersinc.com",
            "mike@monsters inc.com"
    })
    void shouldRejectMalformedEmail(String email) {
        // given
        CreateStudentDTO student = validStudentBuilder().email(email).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    @Test
    void shouldRejectBirthdayInFuture() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.now().plusDays(1)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("birthday");
    }

    @Test
    void shouldRejectBirthdayToday() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.now()).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("birthday");
    }

    @ParameterizedTest
    @ValueSource(strings = {"abcde", "12", "12-34a", "!!-!!!"})
    void shouldRejectMalformedZipCode(String zipCode) {
        // given
        CreateStudentDTO student = validStudentBuilder().zipCode(zipCode).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("zipCode");
    }

    @ParameterizedTest
    @ValueSource(strings = {"abc", "-1", "0"})
    void shouldRejectMalformedHouseNumber(String number) {
        // given
        CreateStudentDTO student = validStudentBuilder().number(number).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("number");
    }

    @ParameterizedTest
    @ValueSource(strings = {"Mike123", "12345", "Mike_Wazowski!"})
    void shouldRejectNameWithDigitsOrSpecialCharacters(String name) {
        // given
        CreateStudentDTO student = validStudentBuilder().name(name).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("name");
    }

    // ---------- SQL injection tests ----------

    @ParameterizedTest
    @MethodSource("sqlInjectionPayloads")
    void shouldRejectSqlInjectionInName(String name) {
        // given
        CreateStudentDTO student = validStudentBuilder().name(name).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("name");
    }

    @ParameterizedTest
    @MethodSource("sqlInjectionPayloads")
    void shouldRejectSqlInjectionInStreet(String street) {
        // given
        CreateStudentDTO student = validStudentBuilder().street(street).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("street");
    }

    @ParameterizedTest
    @MethodSource("sqlInjectionPayloads")
    void shouldRejectSqlInjectionInCity(String city) {
        // given
        CreateStudentDTO student = validStudentBuilder().city(city).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("city");
    }

    @ParameterizedTest
    @MethodSource("sqlInjectionPayloads")
    void shouldRejectSqlInjectionInComplement(String complement) {
        // given
        CreateStudentDTO student = validStudentBuilder().complement(complement).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("complement");
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "mike.wazowski@monstersinc.com' OR '1'='1",
            "mike.wazowski@monstersinc.com'; DROP TABLE student; --",
            "admin'--@monstersinc.com"
    })
    void shouldRejectSqlInjectionInEmail(String email) {
        // given
        CreateStudentDTO student = validStudentBuilder().email(email).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    // ---------- XSS tests ----------

    @ParameterizedTest
    @MethodSource("xssPayloads")
    void shouldRejectScriptInName(String name) {
        // given
        CreateStudentDTO student = validStudentBuilder().name(name).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("name");
    }

    @ParameterizedTest
    @MethodSource("xssPayloads")
    void shouldRejectScriptInStreet(String street) {
        // given
        CreateStudentDTO student = validStudentBuilder().street(street).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("street");
    }

    @ParameterizedTest
    @MethodSource("xssPayloads")
    void shouldRejectScriptInCity(String city) {
        // given
        CreateStudentDTO student = validStudentBuilder().city(city).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("city");
    }

    @ParameterizedTest
    @MethodSource("xssPayloads")
    void shouldRejectScriptInComplement(String complement) {
        // given
        CreateStudentDTO student = validStudentBuilder().complement(complement).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("complement");
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "<script>alert('XSS wykonany')</script>@monstersinc.com",
            "<img src=x onerror=alert(1)>@monstersinc.com",
            "mike@<script>.com"
    })
    void shouldRejectScriptInEmail(String email) {
        // given
        CreateStudentDTO student = validStudentBuilder().email(email).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    // ---------- extreme tests ----------

    @Test
    void shouldAcceptSingleCharacterName() {
        // given
        CreateStudentDTO student = validStudentBuilder().name("M").build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @ParameterizedTest
    @ValueSource(ints = {256, 10_000, 1_000_000})
    void shouldRejectExtremelyLongName(int length) {
        // given
        CreateStudentDTO student = validStudentBuilder().name("a".repeat(length)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("name");
    }

    @Test
    void shouldRejectExtremelyLongStreet() {
        // given
        CreateStudentDTO student = validStudentBuilder().street("x".repeat(10_000)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("street");
    }

    @Test
    void shouldRejectExtremelyLongCity() {
        // given
        CreateStudentDTO student = validStudentBuilder().city("x".repeat(10_000)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("city");
    }

    @Test
    void shouldAcceptEmailLocalPartAtMaximumLength() {
        // given
        CreateStudentDTO student = validStudentBuilder().email("m".repeat(64) + "@monstersinc.com").build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).isEmpty();
    }

    @Test
    void shouldRejectEmailLocalPartAboveMaximumLength() {
        // given
        CreateStudentDTO student = validStudentBuilder().email("m".repeat(65) + "@monstersinc.com").build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    @Test
    void shouldRejectExtremelyLongEmailDomain() {
        // given
        CreateStudentDTO student = validStudentBuilder().email("mike@" + "m".repeat(300) + ".com").build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).containsExactly("email");
    }

    @Test
    void shouldRejectBirthdayMoreThanTwoCenturiesAgo() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.of(1800, 1, 1)).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("birthday");
    }

    @Test
    void shouldRejectMinimalPossibleBirthday() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.MIN).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("birthday");
    }

    @Test
    void shouldRejectMaximalPossibleBirthday() {
        // given
        CreateStudentDTO student = validStudentBuilder().birthday(LocalDate.MAX).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("birthday");
    }

    @ParameterizedTest
    @ValueSource(strings = {"\u0000", "\u202EMike", "🗿"})
    void shouldRejectControlCharactersAndEmojiInName(String name) {
        // given
        CreateStudentDTO student = validStudentBuilder().name(name).build();

        // when
        var invalidFields = invalidFieldsOf(student);

        // then
        assertThat(invalidFields).contains("name");
    }
}
