typedef void*(*GetProcAddress_t)(void*, char*);
typedef void*(*WinExec_t)(char*, unsigned int);

#define SW_SHOW 5

struct RequiredShellcodeData
{
	DWORD hUser32DLL;
	DWORD hKernel32DLL;
	DWORD dwGetProcAddress;
};

void ShellcodeMain(RequiredShellcodeData* shc_data)
{
    GetProcAddress_t getProcAddr = (GetProcAddress_t)shc_data->dwGetProcAddress;
    
    WinExec_t fn = (WinExec_t)getProcAddr(
        (void*)shc_data->hKernel32DLL,
        "WinExec"
    );

    fn("ipconfig", SW_SHOW);
}

int main()
{
	ShellcodeMain(0);
}
