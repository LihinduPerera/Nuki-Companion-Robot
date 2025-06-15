import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Nuki Console',
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: 'Courier',
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.black,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.greenAccent, brightness: Brightness.dark),
      ),
      home: ConsoleScreen(),
    );
  }
}

class ConsoleScreen extends StatefulWidget {
  @override
  _ConsoleScreenState createState() => _ConsoleScreenState();
}

class _ConsoleScreenState extends State<ConsoleScreen> {
  final _channel = WebSocketChannel.connect(
    Uri.parse('ws://192.168.8.200:8765'),
  );

  final List<String> _logs = [];

  @override
  void initState() {
    super.initState();
    _channel.stream.listen((data) {
      setState(() {
        _logs.insert(0, data); // Add new logs at the top
      });
    });
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.black,
        centerTitle: true,
        title: Text(
          "Nuki Console",
          style: TextStyle(
            color: Colors.greenAccent,
            fontSize: 26,
            fontFamily: 'Courier',
            letterSpacing: 1.5,
          ),
        ),
      ),
      body: _logs.isEmpty
          ? Center(
              child: Text(
                'Waiting for logs...',
                style: TextStyle(color: Colors.white54),
              ),
            )
          : ListView.builder(
              reverse: false,
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              itemCount: _logs.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4.0),
                  child: Text(
                    _logs[index],
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontFamily: 'Courier',
                      fontSize: 14,
                    ),
                  ),
                );
              },
            ),
    );
  }
}
