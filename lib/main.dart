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
    Project('Computer Vision - Tuberculosis Quantification', 'assets/ST_A_bacteria_fluorescent.jpg', 'https://samllan.github.io/TuberculosisQuantification'),
    Project('Full Stack - Word Map', 'assets/words_full_stack.png', 'https://samllan.github.io/Words'),
    Project('Fourier Modelling - Weather', 'assets/weather fourier series modelling.webp', 'https://yourusername.github.io/project3'),
    Project('LLM - What Matters To You?', 'assets/line_art_question_heart_LLM_survey.webp', 'https://yourusername.github.io/project4'),
    Project('Computer Vision - Lane Detection', 'assets/lane_detection.jpg', 'https://yourusername.github.io/project5'),
    Project('Generative AI - Med Teacher', 'assets/gen_ai_med_teacher_pexels-cottonbro-7579829.jpg', 'https://yourusername.github.io/project6'),
    Project('Segmenation Classification - Sea Ice Hackathon', 'assets/ice_segmentation.png', 'https://yourusername.github.io/project7'),
    Project('Galactic Signal Mapping - Durham Radio Telescope', 'assets/line_art_radio_telescope.webp', 'https://yourusername.github.io/project8'),
    Project('Founder - AI Society', 'assets/AI at Leeds Logo.png', 'https://aisocietyleeds.wordpress.com/'),
    Project('Founder - AI^2 Society', 'assets/ai2 logo.png', 'https://leeds-ai-cdt.github.io/ai_squared/'),
    Project('Engineering - Strathclyde Boat Record Holder', 'assets/strathclyde boat bulding.jpg', 'https://yourusername.github.io/project11'),
    Project('Kaggle Nature', 'assets/kaggle_nature_hackathon.webp', 'https://yourusername.github.io/project12'),
    Project('Kaggle Health', 'assets/kaggle_health_hackathon.webp', 'https://yourusername.github.io/project13'),
    Project('xAI', 'assets/line_art_explainable_AI.webp', 'https://yourusername.github.io/project14'),
    Project('trad ML', 'assets/trad_ML.webp', 'https://yourusername.github.io/project2'),
    Project('ViT', 'assets/vision_transformer.webp', 'https://yourusername.github.io/project3'),
    Project('Reinforcement Learning', 'assets/line_art_reinforcement_learning_demo_project.webp', 'https://yourusername.github.io/project4'),
    Project('Things That Helped', 'assets/things_i_learnt_pexels-singkham-178541-1108572.jpg', 'https://yourusername.github.io/project5'),
    Project('Train Game', 'assets/train_game.webp', 'https://yourusername.github.io/project6'),
    Project('Events', 'assets/events.webp', 'https://yourusername.github.io/project7'),
    // Project('Paper 1', 'assets/project8-pexels-pixabay-33109.jpg', 'https://yourusername.github.io/project8'),
    // Project('Paper 2', 'assets/project9-pexels-pixabay-60597.jpg', 'https://yourusername.github.io/project9'),
    // Project('Paper 3', 'assets/project10-pexels-pixabay-326055.jpg', 'https://yourusername.github.io/project10'),
    // Project('Project 24', 'assets/project11-pexels-sohi-807598.jpg', 'https://yourusername.github.io/project11'),
    // Project('Project 25', 'assets/project12-pexels-thatguycraig000-1563355.jpg', 'https://yourusername.github.io/project12'),
    // Project('Project 26', 'assets/project13-pexels-vladalex94-1402787.jpg', 'https://yourusername.github.io/project13'),
    // Add more projects here
  ];

  Project? activeProject;

  @override
  void initState() {
    super.initState();
    projects = List.from(projects)..shuffle();
  }

  void setActiveProject(Project? project) {
    setState(() {
      activeProject = project;
    });
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
          project: projects[index],
          isActive: activeProject == projects[index],
          onProjectTap: setActiveProject,
        );
      },
    );
  }
}

class ProjectWidget extends StatefulWidget {
  final Project project;
  final bool isActive;
  final Function(Project?) onProjectTap;

  const ProjectWidget({
    super.key,
    required this.project,
    required this.isActive,
    required this.onProjectTap,
  });

  @override
  ProjectWidgetState createState() => ProjectWidgetState();
}

class ProjectWidgetState extends State<ProjectWidget> {
  bool isHovered = false;

  void _handleTap() {
    if (widget.isActive) {
      _launchURL(widget.project.projectUrl);
    } else {
      widget.onProjectTap(widget.project);
    }
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) {
        if (!widget.isActive) {
          setState(() => isHovered = true);
          widget.onProjectTap(widget.project);
        }
      },
      onExit: (_) {
        if (isHovered) {
          setState(() => isHovered = false);
          widget.onProjectTap(null);
        }
      },
      child: GestureDetector(
        onTap: _handleTap,
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
                color: (isHovered || widget.isActive) ? Colors.black54 : Colors.transparent,
                child: Align(
                  alignment: Alignment.center,
                  child: (isHovered || widget.isActive)
                      ? Text(
                          widget.project.name,
                          style: const TextStyle(color: Colors.white, fontSize: 24),
                          textAlign: TextAlign.center,
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