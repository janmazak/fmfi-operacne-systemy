#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#define BUF_SIZE 1024*1024*1024

char buffer[BUF_SIZE];
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_var = PTHREAD_COND_INITIALIZER;
pthread_cond_t cond_var2 = PTHREAD_COND_INITIALIZER;
int readed = 0;
/*
    Read characters from standard input and saves them to buffer
*/
void *consumer(void *data) {
    int r;
    while(1) {
        //---------CRITICAL CODE--------------
        //------------REGION------------------
        pthread_mutex_lock(&mutex);
        if (readed > 0)
        {
            pthread_cond_wait(&cond_var2, &mutex);
        }
        r = read(0, buffer, BUF_SIZE);
        readed = r;

        pthread_cond_signal(&cond_var);
        pthread_mutex_unlock(&mutex);
        //------------------------------------

        if (r == -1){
            printf("Error reading\n");
        }  
        else if (r == 0) {
            pthread_exit(NULL);
        }
    }
}

/*
    Print chars readed by consumer from standard input to standard output
*/
void *out_producer(void *data) {
    int w;
    while(1){    
        //---------CRITICAL CODE--------------
        //-------------REGION-----------------
        pthread_mutex_lock(&mutex);
        if (readed == 0)
        {
            pthread_cond_wait(&cond_var, &mutex);
        }
        w = write(1, buffer, readed); 
        readed = 0;
        pthread_cond_signal(&cond_var2);
        pthread_mutex_unlock(&mutex);
        //------------------------------------ 

        if (w == -1){
            printf("Error writing\n");
        } 
        else if (w == 0) {
            pthread_exit(NULL);
        }
    }
}


int main() {
    //  Program RETURN value
    int return_value = 0;

    //  in - INPUT thread
    //  out - OUTPUT thread
    pthread_t in, out;

    //  Creating in thread - should read from standard input (0)
    return_value = pthread_create(&in , NULL, consumer, NULL);
    if (return_value != 0) {
        printf("Error creating input thread exiting with code error: %d\n", return_value);
        return return_value;
    }

    //  Creating out thread - should write to standard output (1)
    return_value = pthread_create(&out, NULL, out_producer, NULL);
    if (return_value != 0) {
        printf("Error creating output thread exiting with code error: %d\n", return_value);
        return return_value;
    }

    return_value = pthread_join(in, NULL);
    return_value = pthread_join(out, NULL);

    return return_value;
}

