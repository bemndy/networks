/*
** client.c -- a stream socket client demo
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/stat.h>

#include <arpa/inet.h>

#define MAXDATASIZE 1024 // max number of bytes we can get at once 

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
	if (sa->sa_family == AF_INET) {
		return &(((struct sockaddr_in*)sa)->sin_addr);
	}

	return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(int argc, char *argv[])
{
	int sockfd, numbytes;  
	char buf1[MAXDATASIZE], buf2[MAXDATASIZE];
    char *token;
	struct addrinfo hints, *servinfo, *p;
	int rv;
	char s[INET6_ADDRSTRLEN];

	if (argc != 5) {
	    fprintf(stderr,"usage: filename hostname port authorization\n");
	    exit(1);
	}

    // DEBUG: Display each command-line argument.
    printf( "\nDEBUG: Command-line arguments:\n" );
    for( int i = 0; i < argc; i++ )
        printf( "  argv[%d]   %s\n", i, argv[i] );

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;

	if ((rv = getaddrinfo(argv[2], argv[3], &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	// loop through all the results and connect to the first we can
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((sockfd = socket(p->ai_family, p->ai_socktype,
				p->ai_protocol)) == -1) {
			perror("client: socket");
			continue;
		}

        inet_ntop(p->ai_family,
            get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
        printf("client: attempting connection to %s\n", s);

		if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
			perror("client: connect");
			close(sockfd);
			continue;
		}

		break;
	}

	if (p == NULL) {
		fprintf(stderr, "client: failed to connect\n");
		return 2;
	}

	inet_ntop(p->ai_family,
			get_in_addr((struct sockaddr *)p->ai_addr),
			s, sizeof s);
	printf("client: connected to %s\n", s);

    printf("client: sending INFO %s %s\n", argv[1], argv[4]);

    snprintf(buf1, sizeof(buf1), "INFO %s %s", argv[1], argv[4]);
    if (send(sockfd, buf1, strlen(buf1), 0) == -1) {
        perror("client: send");
        exit(1);
    }

	if ((numbytes = recv(sockfd, buf2, MAXDATASIZE-1, 0)) == -1) {
	    perror("client: recv");
	    exit(1);
	}

	buf2[numbytes] = '\0';

	printf("client: received'%s'\n",buf2);
    token = strtok(buf2, " ");
    token = strtok(NULL, " ");
    if (token == NULL) {
        fprintf(stderr, "client: failed to parse server response: %s\n", buf2);
        exit(1);
    }  else if (strcmp(token, "OK") != 0) {
        fprintf(stderr, "client: server returned error: %s\n", buf2);
        exit(1);
    }

    printf("client: sending GRAB %s %s\n", argv[1], argv[4]);
    snprintf(buf1, sizeof(buf1), "GRAB %s %s", argv[1], argv[4]);
    if (send(sockfd, buf1, strlen(buf1), 0) == -1) {
        perror("client: send");
        exit(1);
    }

    if ((numbytes = recv(sockfd, buf2, MAXDATASIZE-1, 0)) == -1) {
        perror("client: recv");
        exit(1);
    }

    buf2[numbytes] = '\0';

    printf("client: received'%s'\n",buf2);
    token = strtok(buf2, " ");
    token = strtok(NULL, " ");
    if (token == NULL) {
        fprintf(stderr, "client: failed to parse server response: %s\n", buf2);
        exit(1);
    }  else if (strcmp(token, "OK") != 0) {
        fprintf(stderr, "client: server returned error: %s\n", buf2);
        exit(1);
    }

    if ((numbytes = recv(sockfd, buf2, MAXDATASIZE-1, 0)) == -1) {
        perror("client: recv");
        exit(1);
    }

    buf2[numbytes] = '\0';

    struct stat st;
    if (stat("./scans", &st) == -1) {
        mkdir("./scans", 0700);
    }  
    FILE *fp;
    fp = fopen("./scans/test.dat", "w");
    if (fp == NULL) {
        perror("client: fopen");
        exit(1);
    } else {
        fputs(buf2, fp);
        fputs("\n", fp);
        fclose(fp);
    }

    freeaddrinfo(servinfo); // all done with this structure
	close(sockfd);

	return 0;
}