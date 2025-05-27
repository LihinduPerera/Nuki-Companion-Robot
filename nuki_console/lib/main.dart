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
      title: 'Nuki Console',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: ConsoleScreen()
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
        _logs.add(data);
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
        title: Text('Assistant Logs'),
      ),
      body: ListView.builder(
        itemCount: _logs.length,
        itemBuilder: (context, index) {
          return ListTile(
            title: Text(_logs[index]),
          );
        },
      ),
    );
  }
}
