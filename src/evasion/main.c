#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//  ./a.out --encrypt simple_program.exe --output evaded_program.exe --add-size 101 --delay 101

typedef struct s_options {
    const char *input_path;
    const char *output_path;
    long add_size_mb;
    long delay_seconds;
    int show_help;
} t_options;

typedef struct s_buffer {
    unsigned char *data;
    size_t size;
} t_buffer;

typedef struct s_build_context {
    t_options options;
    t_buffer input;
    t_buffer encrypted;
    size_t padding_size;
} t_build_context;

#define DEFAULT_DELAY_SECONDS 101
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

static int parse_args(int argc, char *argv[], t_options *options) {
    int i;
    char *value;

    options->input_path = NULL;
    options->output_path = NULL;
    options->add_size_mb = 0;
    options->delay_seconds = DEFAULT_DELAY_SECONDS;
    options->show_help = 0;
    i = 1;
    while (i < argc) {
        if (strcmp(argv[i], "--help") == 0) {
            options->show_help = 1;
        } else if (i + 1 >= argc ||
                   (argv[i + 1][0] == '-' && argv[i + 1][1] != '\0')) {
            fprintf(stderr, "Error: Missing value for %s.\n", argv[i]);
            return 0;
        } else {
            value = argv[i + 1];
            if (strcmp(argv[i], "--encrypt") == 0) {
                options->input_path = value;
            } else if (strcmp(argv[i], "--output") == 0) {
                options->output_path = value;
            } else if (strcmp(argv[i], "--add-size") == 0) {
                if (!parse_number(value, "--add-size", &options->add_size_mb)) {
                    return 0;
                }
            } else if (strcmp(argv[i], "--delay") == 0) {
                if (!parse_number(value, "--delay", &options->delay_seconds)) {
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

static int validate_options(const t_options *options) {
    if (options->show_help) {
        if (options->input_path != NULL || options->output_path != NULL ||
            options->add_size_mb != 0 ||
            options->delay_seconds != DEFAULT_DELAY_SECONDS) {
            fprintf(stderr,
                    "Error: --help cannot be combined with other options.\n");
            return 0;
        }
    } else if (options->input_path == NULL) {
        fprintf(stderr, "Error: --encrypt <target-binary> is required.\n");
        return 0;
    } else if (options->output_path == NULL) {
        fprintf(stderr, "Error: --output <output-binary> is required.\n");
        return 0;
    } else if (options->add_size_mb != 0 &&
               (options->add_size_mb < MIN_ADD_SIZE_MB ||
                options->add_size_mb > MAX_ADD_SIZE_MB)) {
        fprintf(stderr, "Error: --add-size must be between %d and %d MB.\n",
                MIN_ADD_SIZE_MB, MAX_ADD_SIZE_MB);
        return 0;
    } else if (options->delay_seconds < MIN_DELAY_SECONDS ||
               options->delay_seconds > MAX_DELAY_SECONDS) {
        fprintf(stderr, "Error: --delay must be between %d and %d seconds.\n",
                MIN_DELAY_SECONDS, MAX_DELAY_SECONDS);
        return 0;
    }
    return 1;
}

static void init_buffer(t_buffer *buffer) {
    buffer->data = NULL;
    buffer->size = 0;
}

static void init_context(t_build_context *ctx, const t_options *options) {
    ctx->options = *options;
    init_buffer(&ctx->input);
    init_buffer(&ctx->encrypted);
    ctx->padding_size = 0;
}

static void cleanup_buffer(t_buffer *buffer) {
    free(buffer->data);
    buffer->data = NULL;
    buffer->size = 0;
}

static void cleanup_context(t_build_context *ctx) {
    cleanup_buffer(&ctx->input);
    cleanup_buffer(&ctx->encrypted);
}

static void log_options(const t_options *options) {
    printf("[INFO] Running evasion with the following options:\n");
    printf("[INFO] Input Binary: %s\n", options->input_path);
    printf("[INFO] Output Binary: %s\n", options->output_path);
    if (options->add_size_mb > 0) {
        printf("[INFO] Add Size: %ld MB\n", options->add_size_mb);
    } else {
        printf("[INFO] Add Size: None\n");
    }
    if (options->delay_seconds != DEFAULT_DELAY_SECONDS) {
        printf("[INFO] Delay: %ld seconds\n", options->delay_seconds);
    } else {
        printf("[INFO] Delay: Default (%d seconds)\n", DEFAULT_DELAY_SECONDS);
    }
}

static int load_input_binary(t_build_context *ctx) {
    (void)ctx;
    /*
     * TODO:
     * 1. Open ctx->options.input_path in binary mode.
     * 2. Get the file size.
     * 3. Allocate ctx->input.data.
     * 4. Read the full file into ctx->input.
     */
    fprintf(stderr, "TODO: implement load_input_binary().\n");
    return 0;
}

static int encrypt_input_binary(t_build_context *ctx) {
    (void)ctx;
    /*
     * TODO:
     * 1. Allocate ctx->encrypted.data with the same size as ctx->input.
     * 2. Apply your byte transformation or XOR routine.
     * 3. Store the result in ctx->encrypted.
     */
    fprintf(stderr, "TODO: implement encrypt_input_binary().\n");
    return 0;
}

static int compute_padding_size(t_build_context *ctx) {
    if (ctx->options.add_size_mb <= 0) {
        ctx->padding_size = 0;
        return 1;
    }
    ctx->padding_size = (size_t)ctx->options.add_size_mb * 1024UL * 1024UL;
    return 1;
}

static int write_output_file(const t_build_context *ctx) {
    (void)ctx;
    /*
     * TODO:
     * 1. Open ctx->options.output_path in binary write mode.
     * 2. Write your custom header / metadata.
     * 3. Write ctx->encrypted.data.
     * 4. Append ctx->padding_size bytes if needed.
     */
    fprintf(stderr, "TODO: implement write_output_file().\n");
    return 0;
}

static int process_evasion(const t_options *options) {
    t_build_context ctx;
    int success;

    init_context(&ctx, options);
    log_options(options);
    printf("\n");
    success = load_input_binary(&ctx) && encrypt_input_binary(&ctx) &&
              compute_padding_size(&ctx) && write_output_file(&ctx);
    cleanup_context(&ctx);
    return success;
}

int main(int argc, char *argv[]) {
    t_options options;

    if (argc == 1) {
        print_usage(argv[0]);
        return 1;
    }
    if (!parse_args(argc, argv, &options) || !validate_options(&options)) {
        print_usage(argv[0]);
        return 1;
    }
    if (options.show_help) {
        print_usage(argv[0]);
        return 0;
    }
    if (!process_evasion(&options)) {
        return 1;
    }
    return 0;
}
