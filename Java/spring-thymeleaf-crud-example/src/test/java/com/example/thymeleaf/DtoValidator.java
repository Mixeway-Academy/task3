package com.example.thymeleaf;

import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import com.example.thymeleaf.dto.CreateStudentDTO;

public class DtoValidator {
    
    // Usage:
    //  v.start().setX(x).hasErrors()
    
    private CreateStudentDTO dto;
    private Errors errors;
    private final Validator validator;
    private String last_set_field;

    public DtoValidator(Validator validator) {
        this.validator = validator;
    }

    public DtoValidator start() {
        dto = new CreateStudentDTO();
        errors = new BeanPropertyBindingResult(dto, "dto");
        last_set_field = null;
        return this;
    }

    public DtoValidator setName(String name) {
        this.dto.setName(name);
        this.last_set_field = "name";
        return this;
    }

    public DtoValidator setEmail(String email) {
        this.dto.setEmail(email);
        this.last_set_field = "email";
        return this;
    }

    public DtoValidator setZipCode(String zipCode) {
        this.dto.setZipCode(zipCode);
        this.last_set_field = "zipCode";
        return this;
    }

    public DtoValidator setStreet(String value) {
        this.dto.setStreet(value);
        this.last_set_field = "street";
        return this;
    }

    public DtoValidator setNumber(String value) {
        this.dto.setNumber(value);
        this.last_set_field = "number";
        return this;
    }

    public DtoValidator setComplement(String value) {
        this.dto.setComplement(value);
        this.last_set_field = "complement";
        return this;
    }

    public DtoValidator setDistrict(String value) {
        this.dto.setDistrict(value);
        this.last_set_field = "district";
        return this;
    }

    public DtoValidator setCity(String value) {
        this.dto.setCity(value);
        this.last_set_field = "city";
        return this;
    }

    public DtoValidator setState(String value) {
        this.dto.setState(value);
        this.last_set_field = "state";
        return this;
    }

    public DtoValidator validate() {
        validator.validate(dto, errors);
        return this;
    }

    public int getErrorCount() {
        return errors.getFieldErrorCount(last_set_field);
    }

    public boolean hasErrors() {
        this.validate();
        return errors.getFieldErrorCount(last_set_field) > 0;
    }
}
