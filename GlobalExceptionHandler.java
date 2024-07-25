package com.ceva.spring.announcement.exception;

import java.io.IOException;
import java.util.Date;
import java.util.stream.Collectors;
import javax.validation.ConstraintViolationException;

import org.springframework.data.mapping.PropertyReferenceException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;
import com.ceva.spring.announcement.dto.ResultWrapper;
import com.fasterxml.jackson.databind.exc.InvalidFormatException;

@ControllerAdvice
public class GlobalExceptionHandler {
  /**
   * resource exception handler.
   * 
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(ResourceNotFoundException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> resourceNotFoundException(
      ResourceNotFoundException ex, WebRequest request) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Requested Resource Not Found", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(AnnouncementException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> announcementException(AnnouncementException ex,
      WebRequest request) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(DateFormatException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> dateFormatException(DateFormatException ex,
      WebRequest request) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(IOException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> exception(WebRequest request, Exception ex) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Something went wrong.Please try after sometime", errorDetails);;
    return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(MethodArgumentNotValidException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> methodArgumentInvalidException(
      MethodArgumentNotValidException ex, WebRequest request) {
    String errorMessage = ex.getBindingResult().getFieldErrors().stream()
        .map(error -> error.getDefaultMessage()).findFirst().orElse("Validation error");
    var errorDetails = new ErrorDetails(new Date(), errorMessage, request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(ConstraintViolationException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> methodConstraintDefinitionException(
      ConstraintViolationException ex, WebRequest request) {
    String errorMessage = ex.getConstraintViolations().stream().map(cv -> cv.getMessage())
        .collect(Collectors.joining(", "));
    var errorDetails = new ErrorDetails(new Date(), errorMessage, request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(PropertyReferenceException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> methodPropertyReferenceException(
      PropertyReferenceException ex, WebRequest request) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(InvalidFormatException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> methodInvalidFormatException(
      InvalidFormatException ex, WebRequest request) {
    String message = ex.getPath().stream()
        .map(mapper -> mapper.getFieldName()
            .concat(" value should be of type " + ex.getTargetType().getName()))
        .collect(Collectors.joining("."));
    var errorDetails = new ErrorDetails(new Date(), message, request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
        new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }

  /**
   * resource exception handler.
   *
   * @param ex exception.
   * @param request request.
   * @return response.
   */
  @ExceptionHandler(BindResultException.class)
  public ResponseEntity<ResultWrapper<ErrorDetails>> methodBindResultException(
          BindResultException ex, WebRequest request) {
    var errorDetails = new ErrorDetails(new Date(), ex.getMessage(), request.getDescription(false));
    ResultWrapper<ErrorDetails> response =
            new ResultWrapper<>(false, "Request Validation Failed", errorDetails);
    return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
  }
}
