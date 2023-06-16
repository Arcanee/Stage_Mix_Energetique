#include <stdio.h>
#include <stdlib.h>

//Standard HSV ranges from (0°, 0%, 0%) to (360°, 100%, 100%)
//HSV in opencv ranges from (0, 0, 0) to (180, 255, 255)
//This script makes the conversion from standard to opencv

int main(int argc, char* argv[]) {
    if (argc != 4 && argc != 7) {
        printf("use : ./HSV-convert <H1> <S> <V>\n");
        exit(-1);
    }

    if (argc == 4) {
    float H = atof(argv[1]) / 2;
    float S = atof(argv[2]) / 100 * 255;
    float V = atof(argv[3]) / 100 * 255;

    printf("H: %f\nS: %f\nV: %f\n", H, S, V);
    }

    if (argc == 7) {
    float H1 = atof(argv[1]) / 2;
    float H2 = atof(argv[2]) / 2;

    float S1 = atof(argv[3]) / 100 * 255;
    float S2 = atof(argv[4]) / 100 * 255;
    
    float V1 = atof(argv[5]) / 100 * 255;
    float V2 = atof(argv[6]) / 100 * 255;

    printf("H: %f - %f\nS: %f - %f\nV: %f - %f\n", H1, H2, S1, S2, V1, V2);
    }

    return 0;
}