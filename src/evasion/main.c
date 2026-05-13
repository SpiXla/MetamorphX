#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//  ./a.out --encrypt simple_program.exe --output evaded_program.exe --add-size 101 --delay 101

typedef struct s_args {
    const char *input_path;
    const char *output_path;
    long add_size_mb;
    long delay_seconds;
    int show_help;
} Args;

typedef struct s_binary_data {
    unsigned char *data;
    size_t size;
} Buffer;

typedef struct s_header {
    char magic[4];
    unsigned int version;
    unsigned int payload_size;
    unsigned int padding_size;
    unsigned int key_length;
    unsigned int delay_seconds;
    unsigned char key[256];
} Header;

#define FORMAT_VERSION 1
#define DEFAULT_DELAY_SECONDS 0
#define MIN_ADD_SIZE_MB 1
#define MAX_ADD_SIZE_MB 1024
#define MIN_DELAY_SECONDS 0
#define MAX_DELAY_SECONDS 3600

static void print_usage(const char *program_name) {
    printf("Evasion Program Usage:\n");
    printf("  %s --help\n", program_name);
    printf("  %s --encrypt <target-binary> --output <output-binary> "
           "[--add-size <size-in-mb>] [--delay <seconds>]\n",
           program_name);
    printf("\nOptions:\n");
    printf("  --help                      Show this help message.\n");
    printf("  --encrypt <target-binary>   Encrypt the target binary.\n");
    printf("  --output <output-binary>    Specify the output binary file.\n");
    printf("  --add-size <size-in-mb>     Increase binary size in MB "
           "(%d-%d).\n",
           MIN_ADD_SIZE_MB, MAX_ADD_SIZE_MB);
    printf("  --delay <seconds>           Execution delay in seconds "
           "(default: %d, range: %d-%d).\n",
           DEFAULT_DELAY_SECONDS, MIN_DELAY_SECONDS, MAX_DELAY_SECONDS);
}

static int parse_number(const char *value, const char *flag_name, long *result) {
    char *endptr;

    errno = 0;
    *result = strtol(value, &endptr, 10);
    if (errno == ERANGE || *result < 0) {
        fprintf(stderr, "Error: %s must be a non-negative integer.\n",
                flag_name);
        return 0;
    }
    if (*value == '\0' || *endptr != '\0') {
        fprintf(stderr, "Error: %s must be a valid integer.\n", flag_name);
        return 0;
    }
    return 1;
}

static int parse_args(int argc, char *argv[], Args *args) {
    int i;
    char *value;

    args->input_path = NULL;
    args->output_path = NULL;
    args->add_size_mb = 0;
    args->delay_seconds = DEFAULT_DELAY_SECONDS;
    args->show_help = 0;
    i = 1;
    while (i < argc) {
        if (strcmp(argv[i], "--help") == 0) {
            args->show_help = 1;
        } else if (i + 1 >= argc ||
                   (argv[i + 1][0] == '-' && argv[i + 1][1] != '\0')) {
            fprintf(stderr, "Error: Missing value for %s.\n", argv[i]);
            return 0;
        } else {
            value = argv[i + 1];
            if (strcmp(argv[i], "--encrypt") == 0) {
                args->input_path = value;
            } else if (strcmp(argv[i], "--output") == 0) {
                args->output_path = value;
            } else if (strcmp(argv[i], "--add-size") == 0) {
                if (!parse_number(value, "--add-size", &args->add_size_mb)) {
                    return 0;
                }
            } else if (strcmp(argv[i], "--delay") == 0) {
                if (!parse_number(value, "--delay", &args->delay_seconds)) {
                    return 0;
                }
            } else {
                fprintf(stderr, "Error: Unknown option '%s'.\n", argv[i]);
                return 0;
            }
            i++;
        }
        i++;
    }
    return 1;
}

static int validate_args(const Args *args) {
    if (args->show_help) {
        if (args->input_path != NULL || args->output_path != NULL ||
            args->add_size_mb != 0 ||
            args->delay_seconds != DEFAULT_DELAY_SECONDS) {
            fprintf(stderr,
                    "Error: --help cannot be combined with other options.\n");
            return 0;
        }
    } else if (args->input_path == NULL) {
        fprintf(stderr, "Error: --encrypt <target-binary> is required.\n");
        return 0;
    } else if (args->output_path == NULL) {
        fprintf(stderr, "Error: --output <output-binary> is required.\n");
        return 0;
    } else if (args->add_size_mb != 0 &&
               (args->add_size_mb < MIN_ADD_SIZE_MB ||
                args->add_size_mb > MAX_ADD_SIZE_MB)) {
        fprintf(stderr, "Error: --add-size must be between %d and %d MB.\n",
                MIN_ADD_SIZE_MB, MAX_ADD_SIZE_MB);
        return 0;
    } else if (args->delay_seconds < MIN_DELAY_SECONDS ||
               args->delay_seconds > MAX_DELAY_SECONDS) {
        fprintf(stderr, "Error: --delay must be between %d and %d seconds.\n",
                MIN_DELAY_SECONDS, MAX_DELAY_SECONDS);
        return 0;
    }
    return 1;
}

static void init_buffer(Buffer *buffer) {
    buffer->data = NULL;
    buffer->size = 0;
}

static void cleanup_buffer(Buffer *buffer) {
    free(buffer->data);
    buffer->data = NULL;
    buffer->size = 0;
}

static void log_args(const Args *args) {
    printf("[INFO] Running evasion with the following options:\n");
    printf("[INFO] Input Binary: %s\n", args->input_path);
    printf("[INFO] Output Binary: %s\n", args->output_path);
    if (args->add_size_mb > 0) {
        printf("[INFO] Add Size: %ld MB\n", args->add_size_mb);
    } else {
        printf("[INFO] Add Size: None\n");
    }
    if (args->delay_seconds != DEFAULT_DELAY_SECONDS) {
        printf("[INFO] Delay: %ld seconds\n", args->delay_seconds);
    } else {
        printf("[INFO] Delay: Default (%d seconds)\n", DEFAULT_DELAY_SECONDS);
    }
    printf("\n");
}

static int load_input_binary(const char *input_path, Buffer *input) {
    FILE *file;
    long file_size;
    size_t bytes_read;

    if (input == NULL) {
        fprintf(stderr, "Error: NULL input buffer pointer.\n");
        return 0;
    }

    file = fopen(input_path, "rb");
    if (file == NULL) {
        fprintf(stderr, "Error: Failed to open input file '%s'.\n",
                input_path);
        return 0;
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        fprintf(stderr, "Error: Failed to seek input file '%s'.\n",
                input_path);
        fclose(file);
        return 0;
    }

    file_size = ftell(file);
    if (file_size < 0) {
        fprintf(stderr, "Error: Failed to determine size of '%s'.\n",
                input_path);
        fclose(file);
        return 0;
    }

    if (fseek(file, 0, SEEK_SET) != 0) {
        fprintf(stderr, "Error: Failed to rewind input file '%s'.\n",
                input_path);
        fclose(file);
        return 0;
    }

    input->size = (size_t)file_size;
    if (input->size == 0) {
        input->data = NULL;
        fclose(file);
        return 1;
    }

    input->data = malloc(input->size);
    if (input->data == NULL) {
        fprintf(stderr, "Error: Failed to allocate %zu bytes for input.\n",
                input->size);
        fclose(file);
        return 0;
    }

    bytes_read = fread(input->data, 1, input->size, file);
    if (bytes_read != input->size) {
        fprintf(stderr, "Error: Failed to read input file '%s'.\n",
                input_path);
        cleanup_buffer(input);
        fclose(file);
        return 0;
    }

    fclose(file);
    return 1;
}

static int encrypt_input_binary(const Buffer *input, Buffer *encrypted) {

    size_t i;
    const char *key = "K9x$2LmP#7qZ!4aB";
    if (input == NULL || encrypted == NULL) {
        fprintf(stderr, "Error: NULL buffer pointer.\n");
        return 0;
    }

    encrypted->data = NULL;
    encrypted->size = 0;

    if (input->size > 0 && input->data == NULL) {
        fprintf(stderr, "Error: Input buffer data is NULL.\n");
        return 0;
    }

    encrypted->size = input->size;
    if (encrypted->size == 0) {
        return 1;
    }

    encrypted->data = malloc(encrypted->size);
    if (encrypted->data == NULL) {
        fprintf(stderr, "Error: Failed to allocate %zu bytes.\n",
                encrypted->size);
        return 0;
    }

    for (i = 0; i < encrypted->size; i++) {
        /* put your byte transformation here */
        encrypted->data[i] = input->data[i] ^ key[i % strlen(key)];
    }

    return 1;
}

static size_t compute_padding_size(long add_size_mb) {
    if (add_size_mb <= 0) {
        return 0;
    }

    return (size_t)add_size_mb * 1024UL * 1024UL;
}

static int write_output_file(const char *output_path, const Buffer *encrypted,
                             size_t padding_size, long delay_seconds) {
    const size_t min_padding_size =
        (size_t)MIN_ADD_SIZE_MB * 1024UL * 1024UL;
    const size_t max_padding_size =
        (size_t)MAX_ADD_SIZE_MB * 1024UL * 1024UL;
    FILE *file;
    size_t bytes_written;

    if (output_path == NULL || encrypted == NULL) {
        fprintf(stderr, "Error: NULL output path or encrypted buffer.\n");
        return 0;
    }
    if (encrypted->size > 0 && encrypted->data == NULL) {
        fprintf(stderr, "Error: Encrypted buffer data is NULL.\n");
        return 0;
    }

    if (padding_size > 0 &&
        (padding_size < min_padding_size || padding_size > max_padding_size)) {
        fprintf(stderr, "Error: Padding size is out of bounds.\n");
        return 0;
    }

    if (delay_seconds < MIN_DELAY_SECONDS ||
        delay_seconds > MAX_DELAY_SECONDS) {
        fprintf(stderr, "Error: Delay is out of bounds.\n");
        return 0;
    }

    file = fopen(output_path, "wb");
    if (file == NULL) {
        fprintf(stderr, "Error: Failed to open output file '%s'.\n",
                output_path);
        return 0;
    }
    Header header = {
        .magic = {'E', 'V', 'A', 'D'},
        .version = 1,
        .payload_size = (unsigned int)encrypted->size,
        .padding_size = (unsigned int)padding_size,
        .delay_seconds = (unsigned int)delay_seconds,
        .key = {"K9x$2LmP#7qZ!4aB"},
        .key_length = 16
    };
    bytes_written = fwrite(&header, sizeof(header), 1, file);
    if (bytes_written != 1) {
        fprintf(stderr, "Error: Failed to write header to '%s'.\n",
                output_path);
        fclose(file);
        return 0;
    }

    bytes_written = fwrite(encrypted->data, 1, encrypted->size, file);
    if (bytes_written != encrypted->size) {
        fprintf(stderr, "Error: Failed to write output file '%s'.\n",
                output_path);
        fclose(file);
        return 0;
    }

    if (padding_size > 0) {
        unsigned char *padding = calloc(1, padding_size);
        if (padding == NULL) {
            fprintf(stderr, "Error: Failed to allocate padding.\n");
            fclose(file);
            return 0;
        }
        bytes_written = fwrite(padding, 1, padding_size, file);
        free(padding);
        if (bytes_written != padding_size) {
            fprintf(stderr, "Error: Failed to write padding to '%s'.\n",
                    output_path);
            fclose(file);
            return 0;
        }
    }

    fclose(file);

    size_t file_size = 0;
    Header read_header;
    if (!read_output_file(output_path, &file_size, &read_header)) {
        return 0;
    }

    if (!validate_container_header(file_size, &read_header)) {
        return 0;
    }

    return 1;
}

static int read_output_file(const char *path, size_t *file_size, Header *header){ 
    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        fprintf(stderr, "Error: Failed to open output file '%s'.\n",
                path);
        return 0;  
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        fprintf(stderr, "Error: Failed to seek output file '%s'.\n",
                path);
        fclose(file);
        return 0;
    }

    *file_size = ftell(file);
    if (*file_size < 0) {
        fprintf(stderr, "Error: Failed to determine size of '%s'.\n",
                path);
        fclose(file);
        return 0;
    }

    if (fseek(file, 0, SEEK_SET) != 0) {
        fprintf(stderr, "Error: Failed to rewind output file '%s'.\n",
                path);
        fclose(file);
        return 0;
    }

    if (fread(header, sizeof(Header), 1, file) != 1) {
        fprintf(stderr, "Error: Failed to read header from '%s'.\n",
                path);
        fclose(file);
        return 0;
    }

    fclose(file);
    return 1;
}


static int validate_container_header(size_t actual_file_size,
                                     const Header *header){ 
    size_t expected_size;

    if (header == NULL) {
        fprintf(stderr, "Error: header is NULL.\n");
        return 0;
    }

    if (memcmp(header->magic, "EVAD", 4) != 0) {
        fprintf(stderr, "Error: invalid magic value.\n");
        return 0;
    }

    if (header->version != FORMAT_VERSION) {
        fprintf(stderr, "Error: unsupported version %u.\n", header->version);
        return 0;
    }

    if (header->padding_size > MAX_ADD_SIZE_MB * 1024UL * 1024UL) {
        fprintf(stderr, "Error: padding_size is too large.\n");
        return 0;
    }

    expected_size = sizeof(*header);
    expected_size += (size_t)header->payload_size;
    expected_size += (size_t)header->padding_size;

    if (expected_size < sizeof(header) || expected_size < header->payload_size ||
        expected_size < header->padding_size) {
        fprintf(stderr, "Error: size overflow detected.\n");
        return 0;
    }

    if (expected_size != actual_file_size) {
        fprintf(stderr,
                "Error: truncated or malformed file "
                "(expected %zu bytes, got %zu).\n",
                expected_size, actual_file_size);
        return 0;
    }

    return 1;
}

static int process_evasion(const Args *args) {
    Buffer input;
    Buffer encrypted;
    size_t padding_size;
    int success;

    init_buffer(&input);
    init_buffer(&encrypted);
    log_args(args);
    padding_size = compute_padding_size(args->add_size_mb);
    success = load_input_binary(args->input_path, &input) &&
              encrypt_input_binary(&input, &encrypted) &&
              write_output_file(args->output_path, &encrypted, padding_size,
                                args->delay_seconds);
    cleanup_buffer(&input);
    cleanup_buffer(&encrypted);
    return success;
}

int main(int argc, char *argv[]) {
    Args args;

    if (argc == 1) {
        print_usage(argv[0]);
        return 1;
    }
    if (!parse_args(argc, argv, &args) || !validate_args(&args)) {
        print_usage(argv[0]);
        return 1;
    }
    if (args.show_help) {
        print_usage(argv[0]);
        return 0;
    }
    if (!process_evasion(&args)) {
        return 1;
    }
    return 0;
}
