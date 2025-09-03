# High Level Design (HLD) - Party Drink Tracker

## Overview

The Party Drink Tracker is a web-based application designed to monitor alcohol consumption at parties and estimate Blood Alcohol Content (BAC) levels for safety purposes. The system consists of two main interfaces: a guest interface for drink registration and a host interface for monitoring and safety oversight.

## System Architecture

The application follows a modular Flask architecture with separate interfaces for guests and hosts, running on different ports (4000 and 4001 respectively). The system uses SQLite for data persistence and includes real-time BAC calculations with interactive charting capabilities.

## Class Diagram

```mermaid
classDiagram
    %% Main application classes
    class Guest {
        +int id
        +string name
        +float weight
        +List~Consumption~ drinks
        +calculate_bac() float
        +__repr__() string
    }

    class Drink {
        +int id
        +string name
        +string image_path
        +float abv
        +float volume_ml
        +List~Consumption~ consumptions
        +__repr__() string
    }

    class Consumption {
        +int id
        +int guest_id
        +int drink_id
        +datetime timestamp
        +__repr__() string
    }

    %% Blueprints
    class GuestBlueprint {
        +index() Response
        +select_guest(id) Response
        +add_drink() JSON
    }

    class HostBlueprint {
        +dashboard() Response
        +guest_data() JSON
        +bac_chart(id) JSON
        +group_bac_chart() JSON
    }

    %% Configuration
    class Constants {
        +ETHANOL_DENSITY
        +GENDER_CONSTANT
        +METABOLISM_RATE
        +WEIGHT_CONVERSION
        +BAC_DISPLAY_CAP
        +DECIMAL_PRECISION
    }

    %% Flask framework
    class Flask {
        +create_app()
        +register_blueprint()
        +run()
    }

    %% Relationships
    Guest ||--o{ Consumption : "consumes"
    Drink ||--o{ Consumption : "consumed as"
    GuestBlueprint --> Guest : "manages"
    GuestBlueprint --> Drink : "displays"
    GuestBlueprint --> Consumption : "creates"
    HostBlueprint --> Guest : "monitors"
    HostBlueprint --> Consumption : "analyzes"
    Guest --> Constants : "uses for BAC"
    HostBlueprint --> Constants : "uses for charts"
```

**Note**: `Consumption` represents `DrinkConsumption` class. All constant names have been abbreviated for diagram clarity.

## Use Case Diagrams

### Guest Use Cases

```mermaid
graph TD
    A[Guest] --> B[View Available Drinks]
    A --> C[Select Guest Profile]
    A --> D[Update Weight]
    A --> E[Register Drink Consumption]
    A --> F[View Personal BAC]
    
    B --> G[Drink List Display]
    C --> H[Guest Selection Page]
    D --> I[Weight Update Form]
    E --> J[Drink Selection Interface]
    F --> K[BAC Display]
```

### Host Use Cases

```mermaid
graph TD
    A[Host] --> B[Monitor All Guests]
    A --> C[View Individual BAC Charts]
    A --> D[View Group BAC Charts]
    A --> E[Track Consumption Patterns]
    A --> F[Monitor Safety Thresholds]
    
    B --> G[Guest Dashboard]
    C --> H[Individual BAC Timeline]
    D --> I[Group BAC Comparison]
    E --> J[Consumption Statistics]
    F --> K[Legal Limit Indicators]
```

## Sequence Diagrams

### Use Case 1: Guest Registers a Drink

```mermaid
sequenceDiagram
    participant G as Guest
    participant GB as Guest Browser
    participant GS as Guest Server
    participant DB as Database
    participant M as Models
    
    G->>GB: Navigate to guest interface
    GB->>GS: GET /guest/
    GS->>DB: Query guests and drinks
    DB-->>GS: Return guest and drink data
    GS-->>GB: Render guest selection page
    GB-->>G: Display guest list and drinks
    
    G->>GB: Select guest profile
    GB->>GS: GET /guest/select/{guest_id}
    GS->>DB: Query guest and drinks
    DB-->>GS: Return guest and drink data
    GS-->>GB: Render drink selection page
    GB-->>G: Display drink options
    
    G->>GB: Click on drink
    GB->>GS: POST /guest/add_drink
    Note over GB,GS: {guest_id, drink_id}
    GS->>M: Create DrinkConsumption
    M->>DB: Insert consumption record
    DB-->>M: Confirm insertion
    M-->>GS: Return success
    GS-->>GB: JSON success response
    GB-->>G: Show confirmation message
```

### Use Case 2: Host Monitors Guest BAC Levels

```mermaid
sequenceDiagram
    participant H as Host
    participant HB as Host Browser
    participant HS as Host Server
    participant DB as Database
    participant M as Models
    participant C as Chart Engine
    
    H->>HB: Navigate to host dashboard
    HB->>HS: GET /host/
    HS->>DB: Query all guests
    DB-->>HS: Return guest data
    HS-->>HB: Render dashboard
    HB-->>H: Display guest overview
    
    HB->>HS: GET /host/guest_data
    HS->>DB: Query guests and consumptions
    DB-->>HS: Return consumption data
    HS->>M: Calculate BAC for each guest
    M-->>HS: Return BAC calculations
    HS-->>HB: JSON guest data with BAC
    HB-->>H: Update guest statistics
    
    HB->>HS: GET /host/group_bac_chart
    HS->>DB: Query guests with weight and drinks
    DB-->>HS: Return valid guest data
    HS->>M: Calculate BAC timeline for each guest
    M-->>HS: Return BAC timeline data
    HS->>C: Generate Plotly chart
    C-->>HS: Return chart JSON
    HS-->>HB: JSON chart data
    HB->>C: Render interactive chart
    C-->>HB: Display BAC timeline chart
    HB-->>H: Show group BAC visualization
```

### Use Case 3: BAC Calculation Process

```mermaid
sequenceDiagram
    participant S as System
    participant M as Guest Model
    participant C as Constants
    participant DC as DrinkConsumption
    participant D as Drink
    
    S->>M: calculate_bac()
    M->>M: Check if weight > 0
    alt Weight not set
        M-->>S: Return 0.0
    else Weight is valid
        M->>C: Get gender constant
        C-->>M: Return AVERAGE_GENDER_CONSTANT
        M->>M: Initialize total_alcohol_grams = 0
        M->>M: Get current time
        
        loop For each drink consumption
            M->>DC: Get consumption timestamp
            DC-->>M: Return timestamp
            M->>D: Get drink ABV and volume
            D-->>M: Return ABV and volume_ml
            M->>C: Get ethanol density
            C-->>M: Return ETHANOL_DENSITY_G_PER_ML
            M->>M: Calculate alcohol_grams
            M->>M: Calculate hours_elapsed
            M->>C: Get metabolism rate
            C-->>M: Return BAC_METABOLISM_RATE
            M->>M: Calculate remaining_alcohol
            M->>M: Add to total_alcohol_grams
        end
        
        M->>C: Get conversion factor
        C-->>M: Return LBS_TO_KG_CONVERSION
        M->>M: Convert weight to kg
        M->>M: Calculate BAC percentage
        M->>C: Get display cap and precision
        C-->>M: Return BAC_DISPLAY_CAP and BAC_DECIMAL_PRECISION
        M->>M: Apply cap and round result
        M-->>S: Return final BAC value
    end
```

### Use Case 4: System Initialization

```mermaid
sequenceDiagram
    participant U as User
    participant S as Setup Script
    participant V as Virtual Environment
    participant P as Package Manager
    participant I as Init Script
    participant DB as Database
    participant F as File System
    
    U->>S: Run setup.py
    S->>V: Check if venv exists
    alt Virtual environment not found
        S->>V: Create virtual environment
        V-->>S: Confirm creation
        S-->>U: Display activation instructions
    else Virtual environment exists
        S->>P: Install requirements.txt
        P-->>S: Confirm installation
        S->>I: Run init_sample_data.py
        I->>F: Create ~/guest-list file
        F-->>I: Confirm file creation
        I->>F: Create ~/drinks/drink-list.csv
        F-->>I: Confirm CSV creation
        I->>F: Create placeholder images
        F-->>I: Confirm image creation
        I->>DB: Initialize database tables
        DB-->>I: Confirm table creation
        I->>DB: Insert sample data
        DB-->>I: Confirm data insertion
        I-->>S: Confirm initialization
        S-->>U: Display completion message
    end
```

## Component Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        GI[Guest Interface<br/>Port 4000]
        HI[Host Interface<br/>Port 4001]
    end
    
    subgraph "Application Layer"
        GB[Guest Blueprint]
        HB[Host Blueprint]
        AM[Application Models]
        AC[Application Constants]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        FS[File System<br/>Guest List & Drink Data]
        IM[Image Storage]
    end
    
    subgraph "External Services"
        CH[Chart Engine<br/>Plotly]
        BR[Browser]
    end
    
    GI --> GB
    HI --> HB
    GB --> AM
    HB --> AM
    AM --> DB
    AM --> FS
    AM --> IM
    HB --> CH
    CH --> BR
    AC --> AM
    AC --> HB
```

## Data Flow Architecture

```mermaid
flowchart TD
    A[Guest List File] --> B[Guest Model]
    C[Drink List CSV] --> D[Drink Model]
    E[Drink Images] --> F[Static Assets]
    
    B --> G[Guest Interface]
    D --> G
    F --> G
    
    G --> H[Drink Consumption]
    H --> I[Database]
    
    I --> J[Host Interface]
    J --> K[BAC Calculation]
    K --> L[Chart Generation]
    L --> M[Visualization]
    
    N[Constants] --> K
    N --> L
```

## Security Considerations

- **Input Validation**: All user inputs are validated before database operations
- **SQL Injection Prevention**: Uses SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Flask-WTF provides CSRF protection and input sanitization
- **Data Privacy**: Guest data is stored locally and not transmitted externally
- **Access Control**: Host interface should be protected in production environments

## Performance Considerations

- **Database Optimization**: Uses SQLite with proper indexing on foreign keys
- **Chart Rendering**: Plotly charts are generated server-side and cached
- **Static Assets**: Images and CSS are served efficiently through Flask static routing
- **Memory Management**: BAC calculations are performed on-demand to minimize memory usage

## Scalability Considerations

- **Database Migration**: Easy migration path to PostgreSQL or MySQL for larger deployments
- **Load Balancing**: Multiple server instances can be deployed behind a load balancer
- **Caching**: Redis can be integrated for session management and chart caching
- **Microservices**: Components can be separated into independent services if needed

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        WS1[Web Server 1<br/>Guest Interface]
        WS2[Web Server 2<br/>Host Interface]
        DB[(Production Database)]
        FS[File Storage]
    end
    
    subgraph "Development Environment"
        DS[Development Server]
        DD[(Development Database)]
        DF[Local File Storage]
    end
    
    LB --> WS1
    LB --> WS2
    WS1 --> DB
    WS2 --> DB
    WS1 --> FS
    WS2 --> FS
    
    DS --> DD
    DS --> DF
```

## Technology Stack

- **Backend**: Python 3.12, Flask 2.3.3, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Charts**: Plotly.js
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **Image Processing**: Pillow (PIL)
- **Deployment**: Gunicorn, Nginx (production)

## Future Enhancements

- **Real-time Updates**: WebSocket integration for live BAC monitoring
- **Mobile App**: React Native or Flutter mobile application
- **Advanced Analytics**: Machine learning for consumption pattern analysis
- **Integration**: API endpoints for third-party integrations
- **Multi-party Support**: Support for multiple simultaneous parties
- **Advanced BAC Models**: Gender-specific and food consumption factors
