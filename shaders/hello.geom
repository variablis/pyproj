#version 330

layout (lines) in;                              // now we can access 2 vertices
layout (triangle_strip, max_vertices = 4) out;  // always (for now) producing 2 triangles (so 4 vertices)

// uniform vec2  u_viewportSize = vec2(512,512);
uniform vec2  viewportsize;
uniform float u_thickness = 1.25;

in vec4 v_color[];
out vec4 g_color;

void main()
{
    vec4 p1 = gl_in[0].gl_Position;
    vec4 p2 = gl_in[1].gl_Position;

    vec2 dir    = normalize((p2.xy/p2.w - p1.xy/p1.w) * viewportsize);
    vec2 offset = vec2(-dir.y, dir.x) * u_thickness / viewportsize;

    gl_Position = p1 + vec4(offset.xy * p1.w, 0.0, 0.0);
    g_color = v_color[0];
    EmitVertex();

    gl_Position = p1 - vec4(offset.xy * p1.w, 0.0, 0.0);
    g_color = v_color[0];
    EmitVertex();

    gl_Position = p2 + vec4(offset.xy * p2.w, 0.0, 0.0);
    g_color = v_color[0];
    EmitVertex();

    gl_Position = p2 - vec4(offset.xy * p2.w, 0.0, 0.0);
    g_color = v_color[0];
    EmitVertex();

    EndPrimitive();
}