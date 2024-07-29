import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:math';

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Portfolio - Samuel Llanwarne'),
      ),
      body: ProjectGrid(),
    );
  }
}

class Project {
  final String name;
  final String imageUrl;
  final String projectUrl;

  const Project(this.name, this.imageUrl, this.projectUrl);
}

class ProjectGrid extends StatefulWidget {
  const ProjectGrid({super.key});

  @override
  _ProjectGridState createState() => _ProjectGridState();
}

class _ProjectGridState extends State<ProjectGrid> {
  List<Project> projects = const [
    Project('Project 1', 'assets/project1-nice-clear-light-bulbs-eujn90ms9da1bw9j.jpg', 'https://yourusername.github.io/project1'),
    Project('Project 2', 'assets/project2-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project2'),
    Project('Project 3', 'assets/project3-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project3'),
    Project('Project 4', 'assets/project4-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project4'),
    Project('Project 5', 'assets/project5-pexels-eberhardgross-1366919.jpg', 'https://yourusername.github.io/project5'),
    Project('Project 6', 'assets/project6-pexels-eberhardgross-1624496.jpg', 'https://yourusername.github.io/project6'),
    Project('Project 7', 'assets/project7-pexels-pixabay-33045.jpg', 'https://yourusername.github.io/project7'),
    // Add more projects here
  ];

  @override
  void initState() {
    super.initState();
    projects = List.from(projects)..shuffle();
  }

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(16.0),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3, // 3 tiles per row
        crossAxisSpacing: 16.0, // horizontal spacing
        mainAxisSpacing: 16.0, // vertical spacing
        childAspectRatio: 1.0, // aspect ratio to make them square
      ),
      itemCount: projects.length,
      itemBuilder: (context, index) {
        return ProjectWidget(
          key: GlobalKey<ProjectWidgetState>(),
          project: projects[index],
          onProjectTap: resetAllProjects,
        );
      },
    );
  }

  void resetAllProjects() {
    for (final element in context.findRenderObject()!.visitChildren((child) {
      final state = child as RenderObjectElement;
      final widget = state.widget;
      if (widget is ProjectWidget) {
        final projectWidgetState = widget.key!.currentState as ProjectWidgetState;
        projectWidgetState.reset();
      }
    })) {}
  }
}

class ProjectWidget extends StatefulWidget {
  final Project project;
  final VoidCallback onProjectTap;

  const ProjectWidget({super.key, required this.project, required this.onProjectTap});

  @override
  ProjectWidgetState createState() => ProjectWidgetState();
}

class ProjectWidgetState extends State<ProjectWidget> {
  bool isHovered = false;
  bool isTapped = false;

  void reset() {
    setState(() {
      isTapped = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => isHovered = true),
      onExit: (_) => setState(() => isHovered = false),
      child: GestureDetector(
        onTap: () {
          if (isTapped) {
            _launchURL(widget.project.projectUrl);
          } else {
            widget.onProjectTap();
            setState(() => isTapped = true);
          }
        },
        onLongPress: () {
          _launchURL(widget.project.projectUrl);
        },
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8.0), // Ensures both image and overlay have rounded corners
          child: Stack(
            fit: StackFit.expand,
            children: [
              Image.asset(
                widget.project.imageUrl,
                fit: BoxFit.cover,
              ),
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                color: (isHovered || isTapped) ? Colors.black54 : Colors.transparent,
                child: Center(
                  child: (isHovered || isTapped)
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



// class _ProjectGridState extends State<ProjectGrid> {
//   List<Project> projects = const [
//     Project('Project 1', 'assets/project1-nice-clear-light-bulbs-eujn90ms9da1bw9j.jpg', 'https://yourusername.github.io/project1'),
//     Project('Project 2', 'assets/project2-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project2'),
//     Project('Project 3', 'assets/project3-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project3'),
//     Project('Project 4', 'assets/project4-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project4'),
//     Project('Project 5', 'assets/project5-pexels-eberhardgross-1366919.jpg', 'https://yourusername.github.io/project5'),
//     Project('Project 6', 'assets/project6-pexels-eberhardgross-1624496.jpg', 'https://yourusername.github.io/project6'),
//     Project('Project 7', 'assets/project7-pexels-pixabay-33045.jpg', 'https://yourusername.github.io/project7'),
//     Project('Project 8', 'assets/project8-pexels-pixabay-33109.jpg', 'https://yourusername.github.io/project8'),
//     Project('Project 9', 'assets/project9-pexels-pixabay-60597.jpg', 'https://yourusername.github.io/project9'),
//     Project('Project 10', 'assets/project10-pexels-pixabay-326055.jpg', 'https://yourusername.github.io/project10'),
//     Project('Project 11', 'assets/project11-pexels-sohi-807598.jpg', 'https://yourusername.github.io/project11'),
//     Project('Project 12', 'assets/project12-pexels-thatguycraig000-1563355.jpg', 'https://yourusername.github.io/project12'),
//     Project('Project 13', 'assets/project13-pexels-vladalex94-1402787.jpg', 'https://yourusername.github.io/project13'),
//     Project('Project 14', 'assets/project1-nice-clear-light-bulbs-eujn90ms9da1bw9j.jpg', 'https://yourusername.github.io/project1'),
//     Project('Project 15', 'assets/project2-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project2'),
//     Project('Project 16', 'assets/project3-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project3'),
//     Project('Project 17', 'assets/project4-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project4'),
//     Project('Project 18', 'assets/project5-pexels-eberhardgross-1366919.jpg', 'https://yourusername.github.io/project5'),
//     Project('Project 19', 'assets/project6-pexels-eberhardgross-1624496.jpg', 'https://yourusername.github.io/project6'),
//     Project('Project 20', 'assets/project7-pexels-pixabay-33045.jpg', 'https://yourusername.github.io/project7'),
//     Project('Project 21', 'assets/project8-pexels-pixabay-33109.jpg', 'https://yourusername.github.io/project8'),
//     Project('Project 22', 'assets/project9-pexels-pixabay-60597.jpg', 'https://yourusername.github.io/project9'),
//     Project('Project 23', 'assets/project10-pexels-pixabay-326055.jpg', 'https://yourusername.github.io/project10'),
//     Project('Project 24', 'assets/project11-pexels-sohi-807598.jpg', 'https://yourusername.github.io/project11'),
//     Project('Project 25', 'assets/project12-pexels-thatguycraig000-1563355.jpg', 'https://yourusername.github.io/project12'),
//     Project('Project 26', 'assets/project13-pexels-vladalex94-1402787.jpg', 'https://yourusername.github.io/project13'),
//     // Add more projects here
//   ];

//   @override
//   void initState() {
//     super.initState();
//     projects = List.from(projects)..shuffle();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return GridView.builder(
//       padding: const EdgeInsets.all(16.0),
//       gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
//         crossAxisCount: 3, // 3 tiles per row
//         crossAxisSpacing: 16.0, // horizontal spacing
//         mainAxisSpacing: 16.0, // vertical spacing
//         childAspectRatio: 1.0, // aspect ratio to make them square
//       ),
//       itemCount: projects.length,
//       itemBuilder: (context, index) {
//         return ProjectWidget(project: projects[index]);
//       },
//     );
//   }
// }