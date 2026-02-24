---
id: "spring-pattern-001"
title: "Spring Dependency Injection Patterns"
category: "pattern"
language: "java"
version: "1.0.0"
created_at: "2026-02-24"
tags:
  - spring
  - dependency-injection
  - beans
  - autowired
  - qualifier
  - constructor-injection
---

# Spring Dependency Injection Patterns

## Problem

Spring code with field injection that prevents testing, circular dependencies caused by poor design, ambiguous beans without qualifiers, and incorrect bean scopes causing shared mutable state.

## Solution: Constructor vs Field Injection

Always prefer constructor injection over field injection (`@Autowired` on fields).

```java
// Bad: field injection — cannot instantiate without Spring container, hard to test
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    @Autowired
    private EmailService emailService;
}

// Good: constructor injection — testable, immutable, explicit dependencies
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    // Spring auto-detects single constructor (no @Autowired needed in Spring 4.3+)
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

// Lombok shortcut (recommended):
@Service
@RequiredArgsConstructor  // generates constructor for all final fields
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
}
```

Constructor injection benefits:
- Beans are always fully initialized (no partially constructed objects)
- Dependencies are visible (not hidden in field annotations)
- Easy to unit test — just call `new UserService(mockRepo, mockEmail)`
- Forces you to notice when a class has too many dependencies

## Solution: @Qualifier Usage

When multiple beans of the same type exist, use `@Qualifier` to specify which one to inject.

```java
public interface NotificationService {
    void send(String message, String recipient);
}

@Service("emailNotification")
public class EmailNotificationService implements NotificationService {
    public void send(String message, String recipient) { /* send email */ }
}

@Service("smsNotification")
public class SmsNotificationService implements NotificationService {
    public void send(String message, String recipient) { /* send SMS */ }
}

// Injection with qualifier
@Service
@RequiredArgsConstructor
public class AlertService {
    @Qualifier("emailNotification")
    private final NotificationService notificationService;
}

// Or: inject both and use a Map
@Service
public class AlertService {
    private final Map<String, NotificationService> notificationServices;

    public AlertService(Map<String, NotificationService> notificationServices) {
        this.notificationServices = notificationServices;
    }

    public void alert(String channel, String msg, String recipient) {
        NotificationService svc = notificationServices.get(channel + "Notification");
        if (svc == null) throw new IllegalArgumentException("Unknown channel: " + channel);
        svc.send(msg, recipient);
    }
}
```

## Solution: Circular Dependency Resolution

Circular dependencies are a design smell. Fix them by extracting shared logic.

```java
// Problem: A → B → A
@Service
public class ServiceA {
    public ServiceA(ServiceB b) { /* ... */ }
}

@Service
public class ServiceB {
    public ServiceB(ServiceA a) { /* ... */ }  // circular!
}

// Fix: introduce a SharedService that both depend on
@Service
public class SharedService {
    public void sharedMethod() { /* common logic */ }
}

@Service
@RequiredArgsConstructor
public class ServiceA {
    private final SharedService shared;  // no longer needs B
}

@Service
@RequiredArgsConstructor
public class ServiceB {
    private final SharedService shared;  // no longer needs A
}

// If you cannot refactor, use @Lazy as a last resort
@Service
public class ServiceA {
    private final ServiceB b;
    public ServiceA(@Lazy ServiceB b) { this.b = b; }
}
```

## Solution: Bean Scopes

```java
// Singleton (default): one instance per application context
@Service  // Singleton by default
public class UserService { ... }

// Prototype: new instance every time it's injected
@Component
@Scope("prototype")
public class ReportBuilder { ... }

// Request scope (web): new instance per HTTP request
@Component
@RequestScope
public class RequestContext {
    private String requestId;
    // ...
}

// Caution: injecting a prototype bean into a singleton
// Wrong: prototypeScopeBean will only be created ONCE (singleton behavior)
@Service
@RequiredArgsConstructor
public class SingletonService {
    private final PrototypeService prototypeService;  // only injected once!
}

// Right: use ApplicationContext or ObjectProvider
@Service
@RequiredArgsConstructor
public class SingletonService {
    private final ObjectProvider<PrototypeService> prototypeProvider;

    public void doWork() {
        PrototypeService instance = prototypeProvider.getObject();  // fresh each time
        instance.process();
    }
}
```

## When to Use

- Constructor injection: always, for required dependencies.
- Setter injection: for optional dependencies (rare).
- `@Qualifier`: whenever you have 2+ beans of the same interface.
- `@Primary`: mark the default bean when one is used in 80%+ of injection points.
- `@Scope("prototype")`: for stateful beans that should not be shared.

## When NOT to Use

- Do not use field injection in production code — it prevents testing.
- Do not use `@Autowired` on constructors when there is only one constructor (Spring infers it).
- Do not fix circular dependencies with `@Lazy` without also tracking it as a design debt.

## Related Patterns

- `beh-001` — Code Review Instructions
