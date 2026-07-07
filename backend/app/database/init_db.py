"""Database initialization and seed data management."""
from sqlalchemy.orm import Session
from app.database.session import Base, engine
from app.models.collaborator import CollaboratorProfile, Skill, ProjectInterest, profile_skills, profile_interests


def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def seed_data(db: Session):
    """
    Seed the database with original synthetic collaborator profiles.
    This function is idempotent - it checks for existing data before seeding.
    """
    # Check if data already exists
    if db.query(Skill).count() > 0:
        print("✓ Database already contains seed data, skipping...")
        return
    
    print("Seeding database with synthetic collaborator profiles...")
    
    # Create Skills
    skills_data = [
        # Frontend
        ("React", "frontend"), ("Vue.js", "frontend"), ("Angular", "frontend"),
        ("TypeScript", "frontend"), ("JavaScript", "frontend"), ("HTML/CSS", "frontend"),
        ("Next.js", "frontend"), ("Svelte", "frontend"), ("Redux", "frontend"),
        ("Tailwind CSS", "frontend"), ("Material-UI", "frontend"),
        # Backend
        ("Python", "backend"), ("Node.js", "backend"), ("Java", "backend"),
        ("Go", "backend"), ("Ruby", "backend"), ("PHP", "backend"),
        ("FastAPI", "backend"), ("Django", "backend"), ("Express.js", "backend"),
        ("Spring Boot", "backend"), ("Flask", "backend"),
        # Database
        ("PostgreSQL", "database"), ("MongoDB", "database"), ("MySQL", "database"),
        ("Redis", "database"), ("Elasticsearch", "database"),
        # DevOps
        ("Docker", "devops"), ("Kubernetes", "devops"), ("AWS", "devops"),
        ("Azure", "devops"), ("CI/CD", "devops"), ("Terraform", "devops"),
        ("Jenkins", "devops"),
        # Data & AI
        ("Machine Learning", "data"), ("Data Analysis", "data"), ("TensorFlow", "data"),
        ("PyTorch", "data"), ("Pandas", "data"), ("SQL", "data"),
        # Design
        ("UI/UX Design", "design"), ("Figma", "design"), ("Adobe XD", "design"),
        ("Wireframing", "design"), ("Prototyping", "design"),
        # Mobile
        ("React Native", "mobile"), ("Flutter", "mobile"), ("iOS", "mobile"),
        ("Android", "mobile"),
        # Other
        ("Git", "tools"), ("REST APIs", "tools"), ("GraphQL", "tools"),
        ("Testing", "tools"), ("Agile", "tools"), ("Scrum", "tools")
    ]
    
    skills = []
    for name, category in skills_data:
        skill = Skill(name=name, category=category)
        db.add(skill)
        skills.append(skill)
    db.flush()
    
    # Create Project Interests
    interests_data = [
        ("Web Development", "Building responsive and scalable web applications"),
        ("Mobile Apps", "Creating native and cross-platform mobile applications"),
        ("E-commerce", "Developing online shopping and payment platforms"),
        ("Healthcare Tech", "Building medical and health management systems"),
        ("FinTech", "Financial technology and payment solutions"),
        ("EdTech", "Educational platforms and learning management systems"),
        ("SaaS Products", "Software as a Service business applications"),
        ("DevOps & Infrastructure", "Cloud infrastructure and deployment automation"),
        ("Data Science", "Data analysis, visualization, and insights"),
        ("AI & Machine Learning", "Intelligent systems and predictive models"),
        ("IoT", "Internet of Things and embedded systems"),
        ("Blockchain", "Distributed ledger and cryptocurrency applications"),
        ("Gaming", "Game development and interactive entertainment"),
        ("Social Networks", "Community platforms and social media applications"),
        ("Analytics Dashboards", "Business intelligence and reporting tools"),
        ("API Development", "Building and managing backend services"),
        ("Content Management", "CMS platforms and content delivery systems"),
        ("Cybersecurity", "Security tools and vulnerability management"),
        ("Open Source", "Contributing to community-driven projects"),
        ("Startup MVPs", "Rapid prototyping and minimum viable products")
    ]
    
    interests = []
    for name, description in interests_data:
        interest = ProjectInterest(name=name, description=description)
        db.add(interest)
        interests.append(interest)
    db.flush()
    
    # Helper function to get skill by name
    def get_skill(name):
        try:
            return next(s for s in skills if s.name == name)
        except StopIteration:
            raise ValueError(f"Skill '{name}' not found in skills list. Available skills: {[s.name for s in skills]}")
    
    # Helper function to get interest by name
    def get_interest(name):
        try:
            return next(i for i in interests if i.name == name)
        except StopIteration:
            raise ValueError(f"Interest '{name}' not found in interests list")
    
    # Create 40 diverse synthetic collaborator profiles
    profiles_data = [
        {
            "name": "Sarah Chen",
            "title": "Full-Stack Developer",
            "bio": "Passionate about building scalable web applications with modern frameworks. Love clean code and user-centric design.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC+8",
            "collab": "collaborative", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("React", "advanced"), ("Node.js", "advanced"), ("PostgreSQL", "intermediate"), ("Docker", "intermediate")],
            "interests": ["Web Development", "SaaS Products", "Startup MVPs"]
        },
        {
            "name": "Marcus Johnson",
            "title": "Backend Engineer",
            "bio": "Specialized in building robust APIs and microservices. Strong focus on performance and scalability.",
            "experience": "senior", "years": 7, "availability": 15, "timezone": "UTC-5",
            "collab": "independent", "comm": "async", "team": "medium (4-6)",
            "skills": [("Python", "expert"), ("FastAPI", "expert"), ("PostgreSQL", "advanced"), ("Redis", "advanced"), ("AWS", "intermediate")],
            "interests": ["API Development", "DevOps & Infrastructure", "SaaS Products"]
        },
        {
            "name": "Elena Rodriguez",
            "title": "Frontend Developer",
            "bio": "UI/UX enthusiast who loves creating beautiful and accessible interfaces. Detail-oriented perfectionist.",
            "experience": "mid-level", "years": 3, "availability": 25, "timezone": "UTC+1",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("React", "advanced"), ("TypeScript", "advanced"), ("Tailwind CSS", "advanced"), ("Figma", "intermediate")],
            "interests": ["Web Development", "E-commerce", "Mobile Apps"]
        },
        {
            "name": "David Kim",
            "title": "DevOps Engineer",
            "bio": "Infrastructure automation expert. Making deployments seamless and systems reliable.",
            "experience": "senior", "years": 6, "availability": 10, "timezone": "UTC+9",
            "collab": "flexible", "comm": "async", "team": "medium (4-6)",
            "skills": [("Docker", "expert"), ("Kubernetes", "advanced"), ("AWS", "expert"), ("Terraform", "advanced"), ("CI/CD", "advanced")],
            "interests": ["DevOps & Infrastructure", "Open Source", "API Development"]
        },
        {
            "name": "Priya Patel",
            "title": "Data Scientist",
            "bio": "Turning data into actionable insights. Experienced in ML model development and deployment.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC+5:30",
            "collab": "collaborative", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("Python", "advanced"), ("Machine Learning", "advanced"), ("TensorFlow", "intermediate"), ("Pandas", "advanced"), ("SQL", "advanced")],
            "interests": ["Data Science", "AI & Machine Learning", "Healthcare Tech"]
        },
        {
            "name": "Alex Thompson",
            "title": "Mobile Developer",
            "bio": "Cross-platform mobile app specialist. Building smooth user experiences on iOS and Android.",
            "experience": "mid-level", "years": 5, "availability": 18, "timezone": "UTC-8",
            "collab": "flexible", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("React Native", "advanced"), ("Flutter", "intermediate"), ("TypeScript", "advanced"), ("REST APIs", "advanced")],
            "interests": ["Mobile Apps", "E-commerce", "Social Networks"]
        },
        {
            "name": "Nina Schmidt",
            "title": "UI/UX Designer",
            "bio": "Creating intuitive and delightful user experiences. Research-driven design approach.",
            "experience": "senior", "years": 8, "availability": 15, "timezone": "UTC+2",
            "collab": "collaborative", "comm": "sync", "team": "medium (4-6)",
            "skills": [("UI/UX Design", "expert"), ("Figma", "expert"), ("Prototyping", "advanced"), ("HTML/CSS", "intermediate")],
            "interests": ["Web Development", "Mobile Apps", "SaaS Products"]
        },
        {
            "name": "Raj Malhotra",
            "title": "Full-Stack Engineer",
            "bio": "Polyglot developer comfortable across the entire stack. Quick learner and problem solver.",
            "experience": "senior", "years": 9, "availability": 12, "timezone": "UTC+5:30",
            "collab": "independent", "comm": "async", "team": "large (7+)",
            "skills": [("React", "advanced"), ("Python", "advanced"), ("Django", "advanced"), ("PostgreSQL", "advanced"), ("Docker", "intermediate")],
            "interests": ["Web Development", "API Development", "Open Source"]
        },
        {
            "name": "Sophie Laurent",
            "title": "Junior Frontend Developer",
            "bio": "Recent bootcamp graduate eager to learn and contribute. Enthusiastic about modern web technologies.",
            "experience": "junior", "years": 1, "availability": 30, "timezone": "UTC+1",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("React", "intermediate"), ("JavaScript", "intermediate"), ("HTML/CSS", "advanced"), ("Git", "beginner")],
            "interests": ["Web Development", "Startup MVPs", "Open Source"]
        },
        {
            "name": "Carlos Mendoza",
            "title": "Backend Developer",
            "bio": "Building efficient server-side applications. Strong advocate for test-driven development.",
            "experience": "mid-level", "years": 4, "availability": 22, "timezone": "UTC-3",
            "collab": "flexible", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Node.js", "advanced"), ("Express.js", "advanced"), ("MongoDB", "advanced"), ("REST APIs", "advanced"), ("Testing", "advanced")],
            "interests": ["API Development", "SaaS Products", "E-commerce"]
        },
        {
            "name": "Yuki Tanaka",
            "title": "Tech Lead",
            "bio": "Leading engineering teams to build quality products. Balancing technical excellence with business goals.",
            "experience": "lead", "years": 12, "availability": 10, "timezone": "UTC+9",
            "collab": "flexible", "comm": "hybrid", "team": "large (7+)",
            "skills": [("React", "expert"), ("Node.js", "expert"), ("AWS", "advanced"), ("Agile", "expert"), ("Scrum", "expert")],
            "interests": ["SaaS Products", "Web Development", "Startup MVPs"]
        },
        {
            "name": "Amara Okafor",
            "title": "Cloud Architect",
            "bio": "Designing scalable cloud infrastructure. AWS certified solutions architect.",
            "experience": "senior", "years": 8, "availability": 15, "timezone": "UTC+1",
            "collab": "independent", "comm": "async", "team": "medium (4-6)",
            "skills": [("AWS", "expert"), ("Azure", "advanced"), ("Terraform", "advanced"), ("Kubernetes", "advanced"), ("Python", "intermediate")],
            "interests": ["DevOps & Infrastructure", "SaaS Products", "API Development"]
        },
        {
            "name": "Lucas Silva",
            "title": "Game Developer",
            "bio": "Creating immersive gaming experiences. Specialized in Unity and gameplay mechanics.",
            "experience": "mid-level", "years": 5, "availability": 20, "timezone": "UTC-3",
            "collab": "collaborative", "comm": "sync", "team": "medium (4-6)",
            "skills": [("JavaScript", "advanced"), ("TypeScript", "advanced"), ("Node.js", "intermediate"), ("MongoDB", "intermediate")],
            "interests": ["Gaming", "Mobile Apps", "Web Development"]
        },
        {
            "name": "Emma Wilson",
            "title": "QA Engineer",
            "bio": "Quality assurance specialist. Automated testing and continuous integration expert.",
            "experience": "mid-level", "years": 4, "availability": 25, "timezone": "UTC+0",
            "collab": "collaborative", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Testing", "advanced"), ("Python", "advanced"), ("JavaScript", "intermediate"), ("CI/CD", "advanced"), ("Docker", "advanced")],
            "interests": ["DevOps & Infrastructure", "SaaS Products", "API Development"]
        },
        {
            "name": "Omar Hassan",
            "title": "Blockchain Developer",
            "bio": "Building decentralized applications. Smart contract development and Web3 integration.",
            "experience": "mid-level", "years": 3, "availability": 20, "timezone": "UTC+2",
            "collab": "flexible", "comm": "async", "team": "small (2-3)",
            "skills": [("JavaScript", "advanced"), ("Node.js", "advanced"), ("React", "intermediate"), ("REST APIs", "advanced")],
            "interests": ["Blockchain", "FinTech", "Web Development"]
        },
        {
            "name": "Isabella Rossi",
            "title": "Security Engineer",
            "bio": "Protecting applications from vulnerabilities. Penetration testing and security audits.",
            "experience": "senior", "years": 7, "availability": 12, "timezone": "UTC+1",
            "collab": "independent", "comm": "async", "team": "small (2-3)",
            "skills": [("Python", "advanced"), ("Cybersecurity", "expert"), ("AWS", "intermediate"), ("Docker", "intermediate")],
            "interests": ["Cybersecurity", "DevOps & Infrastructure", "API Development"]
        },
        {
            "name": "Liam O'Brien",
            "title": "Junior Backend Developer",
            "bio": "Starting my journey in backend development. Eager to learn best practices and contribute.",
            "experience": "junior", "years": 1, "availability": 35, "timezone": "UTC+0",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("Python", "beginner"), ("Flask", "beginner"), ("PostgreSQL", "beginner"), ("Git", "beginner")],
            "interests": ["API Development", "Web Development", "Open Source"]
        },
        {
            "name": "Fatima Al-Rashid",
            "title": "Product Engineer",
            "bio": "Bridging product and engineering. Building features that users love.",
            "experience": "mid-level", "years": 5, "availability": 18, "timezone": "UTC+3",
            "collab": "collaborative", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("React", "advanced"), ("TypeScript", "advanced"), ("Node.js", "intermediate"), ("UI/UX Design", "intermediate")],
            "interests": ["SaaS Products", "Startup MVPs", "Mobile Apps"]
        },
        {
            "name": "Zhang Wei",
            "title": "Data Engineer",
            "bio": "Building robust data pipelines. ETL processes and data warehouse design.",
            "experience": "senior", "years": 6, "availability": 15, "timezone": "UTC+8",
            "collab": "flexible", "comm": "async", "team": "medium (4-6)",
            "skills": [("Python", "advanced"), ("SQL", "expert"), ("PostgreSQL", "advanced"), ("AWS", "advanced"), ("Pandas", "advanced")],
            "interests": ["Data Science", "Analytics Dashboards", "API Development"]
        },
        {
            "name": "Olivia Martinez",
            "title": "Frontend Architect",
            "bio": "Designing scalable frontend architectures. Performance optimization specialist.",
            "experience": "lead", "years": 10, "availability": 12, "timezone": "UTC-5",
            "collab": "independent", "comm": "async", "team": "large (7+)",
            "skills": [("React", "expert"), ("TypeScript", "expert"), ("Next.js", "expert"), ("Redux", "expert"), ("Testing", "advanced")],
            "interests": ["Web Development", "SaaS Products", "Open Source"]
        },
        {
            "name": "Henrik Larsson",
            "title": "IoT Developer",
            "bio": "Connecting the physical and digital worlds. Embedded systems and sensor networks.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC+1",
            "collab": "flexible", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("Python", "advanced"), ("Node.js", "intermediate"), ("AWS", "intermediate"), ("REST APIs", "advanced")],
            "interests": ["IoT", "API Development", "Web Development"]
        },
        {
            "name": "Mei Lin",
            "title": "ML Engineer",
            "bio": "Deploying machine learning models at scale. MLOps and model optimization.",
            "experience": "senior", "years": 6, "availability": 15, "timezone": "UTC+8",
            "collab": "independent", "comm": "async", "team": "medium (4-6)",
            "skills": [("Python", "expert"), ("TensorFlow", "advanced"), ("PyTorch", "advanced"), ("Docker", "advanced"), ("AWS", "intermediate")],
            "interests": ["AI & Machine Learning", "Data Science", "Healthcare Tech"]
        },
        {
            "name": "Daniel Cohen",
            "title": "API Developer",
            "bio": "Crafting RESTful and GraphQL APIs. Documentation and developer experience focused.",
            "experience": "mid-level", "years": 4, "availability": 22, "timezone": "UTC+2",
            "collab": "collaborative", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("Node.js", "advanced"), ("GraphQL", "advanced"), ("PostgreSQL", "advanced"), ("REST APIs", "expert"), ("Docker", "intermediate")],
            "interests": ["API Development", "SaaS Products", "Web Development"]
        },
        {
            "name": "Gabriela Santos",
            "title": "Full-Stack Developer",
            "bio": "Versatile developer with strong problem-solving skills. Building end-to-end solutions.",
            "experience": "mid-level", "years": 5, "availability": 20, "timezone": "UTC-3",
            "collab": "flexible", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Vue.js", "advanced"), ("Python", "advanced"), ("Django", "advanced"), ("PostgreSQL", "intermediate"), ("Docker", "intermediate")],
            "interests": ["Web Development", "E-commerce", "Content Management"]
        },
        {
            "name": "Jamal Williams",
            "title": "Junior Mobile Developer",
            "bio": "Learning mobile development with React Native. Building my first production apps.",
            "experience": "junior", "years": 1, "availability": 30, "timezone": "UTC-5",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("React Native", "beginner"), ("JavaScript", "intermediate"), ("React", "intermediate"), ("Git", "beginner")],
            "interests": ["Mobile Apps", "Web Development", "Startup MVPs"]
        },
        {
            "name": "Anja Müller",
            "title": "Platform Engineer",
            "bio": "Building internal developer platforms. Infrastructure as code specialist.",
            "experience": "senior", "years": 7, "availability": 15, "timezone": "UTC+1",
            "collab": "independent", "comm": "async", "team": "large (7+)",
            "skills": [("Kubernetes", "expert"), ("Terraform", "advanced"), ("Docker", "expert"), ("Python", "advanced"), ("AWS", "advanced")],
            "interests": ["DevOps & Infrastructure", "Open Source", "SaaS Products"]
        },
        {
            "name": "Arjun Reddy",
            "title": "FinTech Developer",
            "bio": "Building secure financial applications. Payment integration and compliance expert.",
            "experience": "senior", "years": 6, "availability": 15, "timezone": "UTC+5:30",
            "collab": "flexible", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Java", "advanced"), ("Spring Boot", "advanced"), ("PostgreSQL", "advanced"), ("REST APIs", "advanced"), ("AWS", "intermediate")],
            "interests": ["FinTech", "API Development", "Cybersecurity"]
        },
        {
            "name": "Chloe Anderson",
            "title": "EdTech Developer",
            "bio": "Creating engaging educational experiences. Learning management systems specialist.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC-8",
            "collab": "collaborative", "comm": "sync", "team": "medium (4-6)",
            "skills": [("React", "advanced"), ("Node.js", "intermediate"), ("MongoDB", "intermediate"), ("REST APIs", "advanced")],
            "interests": ["EdTech", "Web Development", "Mobile Apps"]
        },
        {
            "name": "Mohammed Ahmed",
            "title": "Systems Engineer",
            "bio": "Low-level programming and performance optimization. Building efficient systems.",
            "experience": "senior", "years": 8, "availability": 12, "timezone": "UTC+3",
            "collab": "independent", "comm": "async", "team": "small (2-3)",
            "skills": [("Go", "expert"), ("Docker", "advanced"), ("Kubernetes", "advanced"), ("PostgreSQL", "advanced")],
            "interests": ["DevOps & Infrastructure", "API Development", "Open Source"]
        },
        {
            "name": "Sofia Andersson",
            "title": "Growth Engineer",
            "bio": "Data-driven product development. A/B testing and analytics implementation.",
            "experience": "mid-level", "years": 5, "availability": 18, "timezone": "UTC+1",
            "collab": "collaborative", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("React", "advanced"), ("TypeScript", "advanced"), ("Python", "intermediate"), ("Data Analysis", "advanced"), ("SQL", "advanced")],
            "interests": ["Analytics Dashboards", "SaaS Products", "Startup MVPs"]
        },
        {
            "name": "Kwame Nkrumah",
            "title": "Site Reliability Engineer",
            "bio": "Keeping services running smoothly. Monitoring, alerting, and incident response.",
            "experience": "senior", "years": 7, "availability": 10, "timezone": "UTC+0",
            "collab": "flexible", "comm": "async", "team": "large (7+)",
            "skills": [("Python", "advanced"), ("Kubernetes", "advanced"), ("Terraform", "advanced"), ("AWS", "expert"), ("CI/CD", "advanced")],
            "interests": ["DevOps & Infrastructure", "API Development", "SaaS Products"]
        },
        {
            "name": "Luna Park",
            "title": "Healthcare Developer",
            "bio": "Building HIPAA-compliant healthcare applications. Patient data security focused.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC+9",
            "collab": "collaborative", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("React", "advanced"), ("Node.js", "advanced"), ("PostgreSQL", "advanced"), ("AWS", "intermediate")],
            "interests": ["Healthcare Tech", "SaaS Products", "Cybersecurity"]
        },
        {
            "name": "Mateo Hernández",
            "title": "Junior DevOps Engineer",
            "bio": "Learning infrastructure automation. Eager to improve deployment processes.",
            "experience": "junior", "years": 1, "availability": 25, "timezone": "UTC-5",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("Docker", "beginner"), ("Git", "intermediate"), ("Python", "intermediate"), ("CI/CD", "beginner")],
            "interests": ["DevOps & Infrastructure", "Open Source", "API Development"]
        },
        {
            "name": "Aisha Kamara",
            "title": "Integration Engineer",
            "bio": "Connecting systems and services. Third-party API integration specialist.",
            "experience": "mid-level", "years": 5, "availability": 18, "timezone": "UTC+1",
            "collab": "flexible", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Python", "advanced"), ("REST APIs", "expert"), ("GraphQL", "advanced"), ("Node.js", "intermediate"), ("PostgreSQL", "intermediate")],
            "interests": ["API Development", "SaaS Products", "E-commerce"]
        },
        {
            "name": "Ethan Cooper",
            "title": "Analytics Engineer",
            "bio": "Building data models and dashboards. SQL expert and visualization specialist.",
            "experience": "mid-level", "years": 4, "availability": 20, "timezone": "UTC-8",
            "collab": "collaborative", "comm": "hybrid", "team": "small (2-3)",
            "skills": [("SQL", "expert"), ("Python", "advanced"), ("Data Analysis", "advanced"), ("PostgreSQL", "advanced")],
            "interests": ["Analytics Dashboards", "Data Science", "SaaS Products"]
        },
        {
            "name": "Nora Jørgensen",
            "title": "Content Platform Developer",
            "bio": "Building CMS and content delivery systems. Headless CMS architecture specialist.",
            "experience": "mid-level", "years": 5, "availability": 18, "timezone": "UTC+1",
            "collab": "flexible", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("React", "advanced"), ("Node.js", "advanced"), ("MongoDB", "advanced"), ("REST APIs", "advanced"), ("GraphQL", "intermediate")],
            "interests": ["Content Management", "Web Development", "API Development"]
        },
        {
            "name": "Ravi Sharma",
            "title": "Automation Engineer",
            "bio": "Automating repetitive tasks. Testing frameworks and CI/CD pipelines.",
            "experience": "mid-level", "years": 4, "availability": 22, "timezone": "UTC+5:30",
            "collab": "flexible", "comm": "async", "team": "medium (4-6)",
            "skills": [("Python", "advanced"), ("Testing", "advanced"), ("CI/CD", "advanced"), ("Docker", "intermediate"), ("Jenkins", "advanced")],
            "interests": ["DevOps & Infrastructure", "API Development", "Open Source"]
        },
        {
            "name": "Kenji Nakamura",
            "title": "E-commerce Engineer",
            "bio": "Building scalable online shopping platforms. Payment and inventory systems expert.",
            "experience": "senior", "years": 7, "availability": 15, "timezone": "UTC+9",
            "collab": "independent", "comm": "async", "team": "large (7+)",
            "skills": [("React", "advanced"), ("Node.js", "expert"), ("PostgreSQL", "advanced"), ("Redis", "advanced"), ("AWS", "advanced")],
            "interests": ["E-commerce", "SaaS Products", "API Development"]
        },
        {
            "name": "Leila Hassan",
            "title": "Junior Full-Stack Developer",
            "bio": "Enthusiastic learner building full-stack applications. Strong fundamentals and eager to grow.",
            "experience": "junior", "years": 1, "availability": 30, "timezone": "UTC+2",
            "collab": "collaborative", "comm": "sync", "team": "small (2-3)",
            "skills": [("JavaScript", "intermediate"), ("React", "beginner"), ("Node.js", "beginner"), ("HTML/CSS", "advanced"), ("Git", "beginner")],
            "interests": ["Web Development", "Startup MVPs", "Mobile Apps"]
        },
        {
            "name": "Sebastian Kováč",
            "title": "Solutions Architect",
            "bio": "Designing enterprise software solutions. Bridging business needs and technical implementation.",
            "experience": "lead", "years": 11, "availability": 10, "timezone": "UTC+1",
            "collab": "independent", "comm": "hybrid", "team": "large (7+)",
            "skills": [("Java", "expert"), ("AWS", "expert"), ("PostgreSQL", "advanced"), ("Docker", "advanced"), ("Kubernetes", "advanced")],
            "interests": ["SaaS Products", "API Development", "DevOps & Infrastructure"]
        },
        {
            "name": "Maya Patel",
            "title": "Open Source Maintainer",
            "bio": "Contributing to and maintaining open source projects. Community building and code reviews.",
            "experience": "senior", "years": 8, "availability": 15, "timezone": "UTC+5:30",
            "collab": "flexible", "comm": "async", "team": "large (7+)",
            "skills": [("TypeScript", "expert"), ("React", "expert"), ("Node.js", "advanced"), ("Git", "expert"), ("Testing", "advanced")],
            "interests": ["Open Source", "Web Development", "SaaS Products"]
        },
        {
            "name": "Thiago Costa",
            "title": "Social Platform Developer",
            "bio": "Building real-time social features. WebSocket and notification systems.",
            "experience": "mid-level", "years": 5, "availability": 20, "timezone": "UTC-3",
            "collab": "collaborative", "comm": "hybrid", "team": "medium (4-6)",
            "skills": [("Node.js", "advanced"), ("React", "advanced"), ("MongoDB", "advanced"), ("Redis", "intermediate"), ("REST APIs", "advanced")],
            "interests": ["Social Networks", "Web Development", "Mobile Apps"]
        },
        {
            "name": "Ingrid Olsen",
            "title": "Performance Engineer",
            "bio": "Optimizing application performance. Profiling, caching, and database tuning.",
            "experience": "senior", "years": 6, "availability": 12, "timezone": "UTC+1",
            "collab": "independent", "comm": "async", "team": "medium (4-6)",
            "skills": [("Python", "advanced"), ("PostgreSQL", "expert"), ("Redis", "advanced"), ("Docker", "advanced"), ("AWS", "intermediate")],
            "interests": ["API Development", "DevOps & Infrastructure", "SaaS Products"]
        }
    ]
    
    # Create profiles with skills and interests
    for profile_data in profiles_data:
        profile = CollaboratorProfile(
            name=profile_data["name"],
            professional_title=profile_data["title"],
            bio=profile_data["bio"],
            experience_level=profile_data["experience"],
            years_of_experience=profile_data["years"],
            weekly_availability_hours=profile_data["availability"],
            timezone=profile_data["timezone"],
            collaboration_style=profile_data["collab"],
            communication_preference=profile_data["comm"],
            preferred_team_size=profile_data["team"]
        )
        db.add(profile)
        db.flush()
        
        # Add skills to profile
        for skill_name, proficiency in profile_data["skills"]:
            skill = get_skill(skill_name)
            # Use raw SQL to insert with proficiency level
            db.execute(
                profile_skills.insert().values(
                    profile_id=profile.id,
                    skill_id=skill.id,
                    proficiency_level=proficiency
                )
            )
        
        # Add interests to profile
        for interest_name in profile_data["interests"]:
            interest = get_interest(interest_name)
            profile.interests.append(interest)
    
    db.commit()
    print(f"✓ Seeded database with {len(profiles_data)} collaborator profiles")
