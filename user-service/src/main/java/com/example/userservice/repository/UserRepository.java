// user-service/src/main/java/com/example/userservice/repository/UserRepository.java

package com.example.userservice.repository;

import com.example.userservice.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

// @Repository marks this interface as a data repository component.
@Repository
// UserRepository extends JpaRepository, inheriting a wide range of CRUD methods.
// The JpaRepository<User, Long> takes two arguments: the entity class and the data type of its primary key.
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Finds a user by their email address.
     * Spring Data JPA automatically generates the query for this method based on the name.
     * @param email The email to search for.
     * @return An Optional containing the User if found, or empty if not.
     */
    Optional<User> findByEmail(String email);

    /**
     * Finds a user by their username.
     * This method is also automatically implemented by Spring Data JPA.
     * @param username The username to search for.
     * @return An Optional containing the User if found, or empty if not.
     */
    Optional<User> findByUsername(String username);

}
