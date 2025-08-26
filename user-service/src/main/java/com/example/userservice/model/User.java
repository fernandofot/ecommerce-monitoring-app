// user-service/src/main/java/com/example/userservice/model/User.java

package com.example.userservice.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

// @Entity annotation marks this class as a JPA entity, which means it represents a table in the database.
@Entity
// @Table specifies the name of the database table.
@Table(name = "users")
public class User {

    // @Id marks the field as the primary key of the entity.
    @Id
    // @GeneratedValue specifies that the primary key value is automatically generated.
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // @Column maps the field to a column in the database. The 'unique' constraint ensures no two users can have the same email.
    @Column(unique = true, nullable = false)
    private String email;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    // Default constructor for JPA.
    public User() {
        this.createdAt = LocalDateTime.now();
    }

    // Getters and setters for all fields. These are required by JPA.
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
