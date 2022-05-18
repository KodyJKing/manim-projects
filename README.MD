Render a scene with: 
```
manim -pq<qualityLevel: "l" | "h"> <pythonFile> <sceneClassName>
```

Some videos render faster with OpenGL, use the flags:
```
--renderer=opengl --write_to_movie
```

Also, compatibility between the Cairo and OpenGL backends isn't perfect, so some videos have to be rendered with Cairo.