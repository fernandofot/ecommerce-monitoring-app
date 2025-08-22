// user-service/src/main/java/com/example/userservice/UserServiceApplication.java

package com.example.userservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// @SpringBootApplication is a convenience annotation that adds:
// @Configuration: Tags the class as a source of bean definitions for the application context.
// @EnableAutoConfiguration: Tells Spring Boot to start adding beans based on classpath settings.
// @ComponentScan: Tells Spring to look for other components, configurations, and services in the com.example.userservice package,
// allowing it to discover our controller and other classes.
@SpringBootApplication
public class UserServiceApplication {

	public static void main(String[] args) {
		// This is the main method that starts the Spring Boot application.
		SpringApplication.run(UserServiceApplication.class, args);
	}

}
