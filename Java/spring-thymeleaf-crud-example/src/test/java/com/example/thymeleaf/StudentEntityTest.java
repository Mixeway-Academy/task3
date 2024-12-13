package com.example.thymeleaf;

import com.example.thymeleaf.entity.Address;
import com.example.thymeleaf.entity.Student;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDate;

import static org.hibernate.internal.util.StringHelper.repeat;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class StudentEntityTest {

    @Test
    public void testStudentCreation_correctData() {
        assertDoesNotThrow(() -> {
                    Student student = new Student();
                    student.setName("John");
                    student.setBirthday(LocalDate.now());
                    student.setAddress(new Address());
                    student.setEmail("john@gmail.com");
                }
        );
    }

    @Test
    public void testStudentCreation_incorrectNameAndEmail() {
        assertThrows(RuntimeException.class, () -> {
                    Student student = new Student();
                    student.setName("john@gmail.com");
                    student.setBirthday(LocalDate.now());
                    student.setAddress(new Address());
                    student.setEmail("  ");
                }
        );
    }

    @Test
    public void testStudentCreation_XSSInNameAndEmail() {
        assertThrows(RuntimeException.class, () -> {
                    Student student = new Student();
                    student.setName("<script>alert('xss!');</script>");
                    student.setBirthday(LocalDate.now());
                    student.setAddress(new Address());
                    student.setEmail("<script>alert('xss!');</script>");
                }
        );
    }

    @Test
    public void testStudentCreation_SQLInjectionInNameAndEmail() {
        assertThrows(RuntimeException.class, () -> {
                    Student student = new Student();
                    student.setName("-- or # ");
                    student.setBirthday(LocalDate.now());
                    student.setAddress(new Address());
                    student.setEmail("-- or # ");
                }
        );
    }

    @Test
    public void testStudentCreation_extremeDataNameAndEmail() {
        assertThrows(RuntimeException.class, () -> {
                    Student student = new Student();
                    student.setName(repeat("x", 10000));
                    student.setBirthday(LocalDate.now());
                    student.setAddress(new Address());
                    student.setEmail(repeat("x", 10000));
                }
        );
    }
}
