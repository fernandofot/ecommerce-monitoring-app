// user-service/src/main/java/com/example/userservice/controller/UserController.java

package com.example.userservice.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

// @RestController is a convenience annotation for creating RESTful controllers.
@RestController
// @RequestMapping defines the base URL for this controller.
@RequestMapping("/api/auth")
public class UserController {

    // @GetMapping maps HTTP GET requests to the hello() method.
    // The full path for this method will be /api/auth/hello
    @GetMapping("/hello")
    public String hello() {
        return "Hello from the User Service!";
    }
}
