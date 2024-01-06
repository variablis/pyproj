#version 330

layout (points) in;                              // now we can access 2 vertices
layout (triangle_strip, max_vertices = 18) out;  // always (for now) producing 2 triangles (so 4 vertices)

uniform mat4 mvp;
// uniform vec2  u_viewportSize = vec2(512,512);
// uniform vec2  viewportsize;
uniform float zoomfact;
uniform float u_thickness = .75;

in vec4 v_color[];
out vec4 g_color;

void main()
{
    vec4 p1 = gl_in[0].gl_Position;
    // vec4 p2 = gl_in[1].gl_Position;


    // hardcoded array for circle points
    vec2 circlePoints[6] = vec2[]
    (
        vec2(0.02, 0.0),
        vec2(0.01, 0.01732),
        vec2(-0.01, 0.01732),
        vec2(-0.02, 0.0),
        vec2(-0.01, -0.01732),
        vec2(0.01, -0.01732)
    );

    // loop to create a filled hexagon around p1
    for (int i = 0; i < 6; ++i) {
        vec2 hexagonPoint = p1.xy + u_thickness / zoomfact * circlePoints[i];

        gl_Position = mvp*vec4(hexagonPoint, p1.z, p1.w);
        g_color = v_color[0];
        EmitVertex();

        gl_Position = mvp*vec4(p1.xy, p1.z, p1.w);
        g_color = v_color[0];
        EmitVertex();

        hexagonPoint = p1.xy + u_thickness/ zoomfact * circlePoints[(i + 1) % 6];
        gl_Position = mvp*vec4(hexagonPoint, p1.z, p1.w);
        g_color = v_color[0];
        EmitVertex();
    }

    EndPrimitive();
    
}