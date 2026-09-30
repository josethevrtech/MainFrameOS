// MainFrameOS laptop input bridge. MIT. SDL3 receives input only in this window.
#include <SDL3/SDL.h>
#include <linux/input-event-codes.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static int outfd=-1, infd=-1; static pid_t child=-1;
static bool overlay=false;
static bool active=false, connected=false; static SDL_Window *window;
static const char *status="Connecting to Frame...";
static int mapping[SDL_SCANCODE_COUNT];
static bool sendline(const char *line) {
    size_t n=strlen(line); return outfd>=0 && write(outfd,line,n)==(ssize_t)n;
}
static void release_input(void) {
    active=false;
    SDL_SetWindowRelativeMouseMode(window,false);
    SDL_SetWindowKeyboardGrab(window,false);
    sendline("R\n");
}
static void eventline(char type,int a,int b) {
    char line[64]; snprintf(line,sizeof line,"%c %d %d\n",type,a,b);
    if (!sendline(line)) {release_input(); connected=false; status="Connection lost. Close and reopen.";}
}
static void mapkeys(void) {
#define MAP(s,k) mapping[SDL_SCANCODE_##s]=KEY_##k
    int letters[]={KEY_A,KEY_B,KEY_C,KEY_D,KEY_E,KEY_F,KEY_G,KEY_H,KEY_I,KEY_J,KEY_K,KEY_L,KEY_M,KEY_N,KEY_O,KEY_P,KEY_Q,KEY_R,KEY_S,KEY_T,KEY_U,KEY_V,KEY_W,KEY_X,KEY_Y,KEY_Z};
    for(int i=0;i<26;i++) mapping[SDL_SCANCODE_A+i]=letters[i];
    int digits[]={KEY_1,KEY_2,KEY_3,KEY_4,KEY_5,KEY_6,KEY_7,KEY_8,KEY_9,KEY_0};
    for(int i=0;i<10;i++) mapping[SDL_SCANCODE_1+i]=digits[i];
    int fn[]={KEY_F1,KEY_F2,KEY_F3,KEY_F4,KEY_F5,KEY_F6,KEY_F7,KEY_F8,KEY_F9,KEY_F10,KEY_F11,KEY_F12};
    for(int i=0;i<12;i++) mapping[SDL_SCANCODE_F1+i]=fn[i];
    MAP(RETURN,ENTER); MAP(ESCAPE,ESC); MAP(BACKSPACE,BACKSPACE); MAP(TAB,TAB); MAP(SPACE,SPACE);
    MAP(MINUS,MINUS); MAP(EQUALS,EQUAL); MAP(LEFTBRACKET,LEFTBRACE); MAP(RIGHTBRACKET,RIGHTBRACE);
    MAP(BACKSLASH,BACKSLASH); MAP(NONUSBACKSLASH,102ND); MAP(SEMICOLON,SEMICOLON); MAP(APOSTROPHE,APOSTROPHE);
    MAP(GRAVE,GRAVE); MAP(COMMA,COMMA); MAP(PERIOD,DOT); MAP(SLASH,SLASH); MAP(CAPSLOCK,CAPSLOCK);
    MAP(PRINTSCREEN,SYSRQ); MAP(SCROLLLOCK,SCROLLLOCK); MAP(PAUSE,PAUSE); MAP(INSERT,INSERT);
    MAP(HOME,HOME); MAP(PAGEUP,PAGEUP); MAP(DELETE,DELETE); MAP(END,END); MAP(PAGEDOWN,PAGEDOWN);
    MAP(RIGHT,RIGHT); MAP(LEFT,LEFT); MAP(DOWN,DOWN); MAP(UP,UP);
    MAP(LCTRL,LEFTCTRL); MAP(RCTRL,RIGHTCTRL); MAP(LSHIFT,LEFTSHIFT); MAP(RSHIFT,RIGHTSHIFT);
    MAP(LALT,LEFTALT); MAP(RALT,RIGHTALT); MAP(LGUI,LEFTMETA); MAP(RGUI,RIGHTMETA); MAP(APPLICATION,COMPOSE);
    MAP(NUMLOCKCLEAR,NUMLOCK); MAP(KP_DIVIDE,KPSLASH); MAP(KP_MULTIPLY,KPASTERISK); MAP(KP_MINUS,KPMINUS);
    MAP(KP_PLUS,KPPLUS); MAP(KP_ENTER,KPENTER); MAP(KP_PERIOD,KPDOT); MAP(KP_0,KP0);
    int kp[]={KEY_KP1,KEY_KP2,KEY_KP3,KEY_KP4,KEY_KP5,KEY_KP6,KEY_KP7,KEY_KP8,KEY_KP9};
    for(int i=0;i<9;i++) mapping[SDL_SCANCODE_KP_1+i]=kp[i];
#undef MAP
}
static void start(void) {
    if(!connected || active) return;
    if(!SDL_SetWindowRelativeMouseMode(window,true)) {status="Pointer capture failed. Close and retry."; return;}
    if(!SDL_SetWindowKeyboardGrab(window,true)) {SDL_SetWindowRelativeMouseMode(window,false); status="Keyboard capture failed."; return;}
    sendline("R\n"); active=true; status="CONTROLLING STEAM FRAME";
    if(overlay) {puts("ACTIVE");fflush(stdout);}
}
int main(int argc,char **argv) {
    if(argc!=4) {fprintf(stderr,"Usage: client SSH_KEY USER@HOST REMOTE_RECEIVER\n");return 2;}
    signal(SIGPIPE,SIG_IGN); mapkeys();
    overlay=getenv("MAINFRAMEOS_INPUT_OVERLAY")!=NULL;
    int to[2],from[2]; if(pipe(to)||pipe(from)) return 2;
    child=fork();
    if(child==0) {
        dup2(to[0],0); dup2(from[1],1); close(to[0]);close(to[1]);close(from[0]);close(from[1]);
        execlp("ssh","ssh","-T","-o","BatchMode=yes","-o","StrictHostKeyChecking=yes","-o","ConnectTimeout=8","-o","ServerAliveInterval=2","-o","ServerAliveCountMax=2","-i",argv[1],argv[2],"python3",argv[3],(char*)NULL); _exit(127);
    }
    close(to[0]); close(from[1]); outfd=to[1]; infd=from[0];
    fcntl(outfd,F_SETFL,O_NONBLOCK); fcntl(infd,F_SETFL,O_NONBLOCK);
    if(child<0 || !SDL_Init(SDL_INIT_VIDEO)) return 2;
    window=SDL_CreateWindow("Control Steam Frame",820,overlay?130:430,overlay?(SDL_WINDOW_BORDERLESS|SDL_WINDOW_ALWAYS_ON_TOP|SDL_WINDOW_UTILITY):0);
    SDL_Renderer *r=window?SDL_CreateRenderer(window,NULL):NULL;
    if(!r) {fprintf(stderr,"SDL: %s\n",SDL_GetError());close(outfd);kill(child,SIGTERM);return 2;}
    SDL_SetRenderLogicalPresentation(r,410,overlay?65:215,SDL_LOGICAL_PRESENTATION_LETTERBOX);
    Uint64 last_ping=0,last_ack=SDL_GetTicks(); bool running=true; char reply[128], incoming[256]={0}; size_t used=0;
    float mx=0,my=0,wx=0,wy=0;
    Uint64 born=SDL_GetTicks(); bool started=false;
    while(running) {
        ssize_t got=read(infd,reply,sizeof(reply)-1);
        if(got>0) {
            if(used+(size_t)got>=sizeof incoming) {release_input();running=false;continue;}
            memcpy(incoming+used,reply,(size_t)got);used+=(size_t)got;incoming[used]=0;
            char *newline;
            while((newline=strchr(incoming,'\n'))) {
                *newline=0;
                if(!strcmp(incoming,"P") || !strcmp(incoming,"READY")) last_ack=SDL_GetTicks();
                if(!strcmp(incoming,"READY")) {connected=true;status="Ready. Input stays on your laptop.";}
                size_t consumed=(size_t)(newline-incoming)+1;
                memmove(incoming,incoming+consumed,used-consumed);used-=consumed;incoming[used]=0;
            }
        }
        else if(got==0) {release_input();connected=false; status="Disconnected. Close and reopen to retry.";}
        if(SDL_GetTicks()-last_ping>500) {sendline("P\n");last_ping=SDL_GetTicks();}
        if(connected && SDL_GetTicks()-last_ack>3000) {release_input();connected=false;status="Connection timed out. Laptop control restored.";}
        SDL_Event e;
        while(SDL_PollEvent(&e)) {
            if(e.type==SDL_EVENT_QUIT) {running=false;break;}
            if(e.type==SDL_EVENT_WINDOW_FOCUS_LOST) {if(overlay && active) running=false;release_input();status="Paused. Click this window, then press Space.";}
            if(overlay && e.type==SDL_EVENT_KEY_DOWN && e.key.scancode==SDL_SCANCODE_F11 && !e.key.repeat) {release_input();running=false;continue;}
            if(e.type==SDL_EVENT_KEY_DOWN && e.key.scancode==SDL_SCANCODE_ESCAPE && (e.key.mod&SDL_KMOD_CTRL) && (e.key.mod&SDL_KMOD_ALT)) {release_input();if(overlay) running=false;status="Paused. Input is back on your laptop.";continue;}
            if(!active) {
                if(e.type==SDL_EVENT_KEY_DOWN && e.key.scancode==SDL_SCANCODE_SPACE && !e.key.repeat) start();
                if(e.type==SDL_EVENT_MOUSE_BUTTON_UP && e.button.button==SDL_BUTTON_LEFT) start();
                continue;
            }
            if((e.type==SDL_EVENT_KEY_DOWN || e.type==SDL_EVENT_KEY_UP) && !e.key.repeat && e.key.scancode<SDL_SCANCODE_COUNT) {
                int key=mapping[e.key.scancode]; if(key) eventline('K',key,e.type==SDL_EVENT_KEY_DOWN);
            } else if(e.type==SDL_EVENT_MOUSE_MOTION) {
                mx+=e.motion.xrel;my+=e.motion.yrel;
                int x=(int)mx,y=(int)my;mx-=x;my-=y;
                if(x || y) eventline('M',SDL_clamp(x,-4096,4096),SDL_clamp(y,-4096,4096));
            } else if(e.type==SDL_EVENT_MOUSE_BUTTON_DOWN || e.type==SDL_EVENT_MOUSE_BUTTON_UP) {
                int b=0;
                switch(e.button.button) {case SDL_BUTTON_LEFT:b=BTN_LEFT;break;case SDL_BUTTON_RIGHT:b=BTN_RIGHT;break;case SDL_BUTTON_MIDDLE:b=BTN_MIDDLE;break;case SDL_BUTTON_X1:b=BTN_SIDE;break;case SDL_BUTTON_X2:b=BTN_EXTRA;break;}
                if(b) eventline('B',b,e.type==SDL_EVENT_MOUSE_BUTTON_DOWN);
            } else if(e.type==SDL_EVENT_MOUSE_WHEEL) {
                float sign=e.wheel.direction==SDL_MOUSEWHEEL_FLIPPED?-1:1;
                wx+=e.wheel.x*sign;wy+=e.wheel.y*sign;
                int x=(int)wx,y=(int)wy;wx-=x;wy-=y;
                if(x || y) eventline('W',SDL_clamp(x,-120,120),SDL_clamp(y,-120,120));
            }
        }
        if(overlay && connected && !started && (SDL_GetWindowFlags(window)&SDL_WINDOW_INPUT_FOCUS)) {
            started=true;start();if(!active) {puts("ERROR: Input capture failed");fflush(stdout);running=false;}
        }
        if(overlay && SDL_GetTicks()-born>10000 && !started) {puts("ERROR: Connection or window focus unavailable");fflush(stdout);running=false;}
        if(overlay && started && !connected) {puts("ERROR: Headset connection lost");fflush(stdout);running=false;}
        SDL_SetRenderDrawColor(r,18,24,33,255);SDL_RenderClear(r);
        if(overlay) {
            SDL_SetRenderDrawColor(r,90,235,165,255);
            SDL_RenderDebugText(r,15,12,active?"STEAM FRAME CONTROL":"CONNECTING TO STEAM FRAME...");
            SDL_SetRenderDrawColor(r,225,230,240,255);
            SDL_RenderDebugText(r,15,34,"F11 or Ctrl+Alt+Escape: return to laptop");
            SDL_RenderPresent(r);SDL_Delay(8);continue;
        }
        SDL_SetRenderDrawColor(r,active?90:180,active?235:200,active?165:220,255);
        SDL_RenderDebugText(r,18,20,"MAINFRAMEOS / FRAME INPUT");
        SDL_RenderDebugText(r,18,52,status);
        SDL_SetRenderDrawColor(r,225,230,240,255);
        SDL_RenderDebugText(r,18,86,"Click here or press Space to take control.");
        SDL_RenderDebugText(r,18,108,"Keyboard + touchpad go to native Frame apps.");
        SDL_RenderDebugText(r,18,140,"Ctrl + Alt + Escape = return to laptop");
        SDL_RenderDebugText(r,18,164,"Closing this window also releases control.");
        SDL_RenderDebugText(r,18,188,"Encrypted Wi-Fi connection. No screen stream.");
        SDL_RenderPresent(r);SDL_Delay(8);
    }
    release_input(); close(outfd);close(infd);kill(child,SIGTERM);waitpid(child,NULL,0);
    SDL_DestroyRenderer(r);SDL_DestroyWindow(window);SDL_Quit();return 0;
}
