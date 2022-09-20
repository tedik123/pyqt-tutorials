#version 120

// input variable, which was an output variable to the fragment shader
varying lowp vec4 color;

void main(void) {
// this tells what color the fragement should be
    gl_FragColor = color;
                }