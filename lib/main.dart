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
    Project('Project 3', 'assets/project3-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project3'),
    Project('Project 4', 'assets/project4-pexels-eberhardgross-443446.jpg', 'https://yourusername.github.io/project4'),
    Project('Project 5', 'assets/project5-pexels-eberhardgross-1366919.jpg', 'https://yourusername.github.io/project5'),
    Project('Project 6', 'assets/project6-pexels-eberhardgross-1624496.jpg', 'https://yourusername.github.io/project6'),
    Project('Project 7', 'assets/project7-pexels-pixabay-33045.jpg', 'https://yourusername.github.io/project7'),
    Project('Project 8', 'assets/project8-pexels-pixabay-33109.jpg', 'https://yourusername.github.io/project8'),
    Project('Project 9', 'assets/project9-pexels-pixabay-60597.jpg', 'https://yourusername.github.io/project9'),
    Project('Project 10', 'assets/project10-pexels-pixabay-326055.jpg', 'https://yourusername.github.io/project10'),
    Project('Project 11', 'assets/project11-pexels-sohi-807598.jpg', 'https://yourusername.github.io/project11'),
    Project('Project 12', 'assets/project12-pexels-thatguycraig000-1563355.jpg', 'https://yourusername.github.io/project12'),
    Project('Project 13', 'assets/project13-pexels-vladalex94-1402787.jpg', 'https://yourusername.github.io/project13'),
    Project('Project 14', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project14'),
    Project('Project 15', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project15'),
    Project('Project 16', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project16'),
    Project('Project 17', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project17'),
    Project('Project 18', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project18'),
    Project('Project 19', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project19'),
    Project('Project 20', 'assets/project1-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project20'),
    // Add more projects here
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Portfolio - Samuel Llanwarne'),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(16.0),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3, // 3 tiles per row
          crossAxisSpacing: 16.0, // horizontal spacing
          mainAxisSpacing: 16.0, // vertical spacing
          childAspectRatio: 1.0, // aspect ratio to make them square
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
        child: Container(
          decoration: BoxDecoration(
            image: DecorationImage(
              image: AssetImage(widget.project.imageUrl),
              fit: BoxFit.cover,
            ),
            borderRadius: BorderRadius.circular(8.0), // Optional: Adds rounded corners
          ),
          child: AnimatedContainer(
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




// class ProjectGrid extends StatelessWidget {
//   final List<Project> projects = const [
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
//     Project('Project 14', 'assets/project14-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project14'),
//     Project('Project 15', 'assets/project15-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project15'),
//     Project('Project 16', 'assets/project16-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project16'),
//     Project('Project 17', 'assets/project17-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project17'),
//     Project('Project 18', 'assets/project18-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project18'),
//     Project('Project 19', 'assets/project19-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project19'),
//     Project('Project 20', 'assets/project20-3cb45f6e59190e8213ce0a35394d0e11-nice.jpg', 'https://yourusername.github.io/project20'),
//     // Add more projects here
//   ];

//   ProjectGrid({super.key}) {
//     projects.shuffle(Random());
//   }

//   @override
//   Widget build(BuildContext context) {
//     return GridView.builder(
//       padding: const EdgeInsets.all(16.0),
//       gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
//         crossAxisCount: 3, // 3 tiles per row
//         crossAxisSpacing: 16.0, // horizontal spacing
//         mainAxisSpacing: 16.0, // vertical spacing
//         childAspectRatio: 1.0, // aspect ratio to make them square and to control height
//       ),
//       itemCount: projects.length,
//       itemBuilder: (context, index) {
//         return ProjectWidget(project: projects[index]);
//       },
//     );
//   }
// }