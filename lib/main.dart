import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Portfolio',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const PortfolioPage(),
    );
  }
}

class PortfolioPage extends StatelessWidget {
  const PortfolioPage({super.key});

  final List<Project> projects = const [
    Project('Project 1', 'assets/project1-nice-clear-light-bulbs-eujn90ms9da1bw9j.jpg', 'https://yourusername.github.io/project1'),
    Project('Project 2', 'assets/project2-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project2'),
    // Add more projects here
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Portfolio'),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(16.0),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3, // 3 tiles per row
          crossAxisSpacing: 16.0, // horizontal spacing
          mainAxisSpacing: 16.0, // vertical spacing
          childAspectRatio: 1.5, // aspect ratio to control height
        ),
        itemCount: projects.length,
        itemBuilder: (context, index) {
          return ProjectWidget(project: projects[index]);
        },
      ),
    );
  }
}

class Project {
  final String name;
  final String imageUrl;
  final String projectUrl;

  const Project(this.name, this.imageUrl, this.projectUrl);
}

class ProjectWidget extends StatefulWidget {
  final Project project;

  const ProjectWidget({super.key, required this.project});

  @override
  ProjectWidgetState createState() => ProjectWidgetState();
}

class ProjectWidgetState extends State<ProjectWidget> {
  bool isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: GestureDetector(
        onTap: () => _launchURL(widget.project.projectUrl),
        child: Stack(
          children: [
            Image.asset(widget.project.imageUrl, fit: BoxFit.cover),
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              color: isHovered ? Colors.black54 : Colors.transparent,
              child: Center(
                child: isHovered
                    ? Text(
                        widget.project.name,
                        style: const TextStyle(color: Colors.white, fontSize: 24),
                      )
                    : Container(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _launchURL(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    } else {
      throw 'Could not launch $url';
    }
  }
}