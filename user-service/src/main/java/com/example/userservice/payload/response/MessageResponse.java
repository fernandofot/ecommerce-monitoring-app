// user-service/src/main/java/com/example/userservice/payload/response/MessageResponse.java

package com.example.userservice.payload.response;

// This DTO is a generic response for simple messages, like success or error confirmations.
public class MessageResponse {

    private String message;

    public MessageResponse(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
