#include <Windows.h>
#include <stdio.h>
#include <memory>

const char shellcode[] = "\x55\x89\xE5\x83\xEC\x08\x8B\x45\x08\x8B\x48\x08\x89\x4D\xFC\x6A\x00\x68\x78\x65\x63\x00\x68\x57\x69\x6E\x45\x89\xE6\x56\x8B\x55\x08\x8B\x42\x04\x50\xFF\x55\xFC\x83\xC4\x08\x89\x45\xF8\x6A\x00\x68\x6E\x66\x69\x67\x68\x69\x70\x63\x6F\x89\xE6\x6A\x05\x56\xFF\x55\xF8\x83\xC4\x08\x89\xEC\x5D\xC2\x00\x00";

struct RequiredShellcodeData
{
	DWORD hUser32DLL;
	DWORD hKernel32DLL;
	DWORD dwGetProcAddress;
};

int execute_shellcode(RequiredShellcodeData* sch_data)
{
	PVOID shellcode_exec = VirtualAlloc(0, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	if (!shellcode_exec)
	{
		printf("Failed to allocate memory for shellcode execution\n");
		return -3;
	}

	RtlCopyMemory(shellcode_exec, shellcode, sizeof(shellcode));

	DWORD threadID;
	HANDLE hThread = CreateThread(NULL, 0, (PTHREAD_START_ROUTINE)shellcode_exec, sch_data, 0, &threadID);
	if (!hThread)
	{
		printf("Failed to create thread with CreateThread");
		return -5;
	}

	WaitForSingleObject(hThread, INFINITE);

	return 0;
}

int main()
{
	HMODULE hUser32DLL = LoadLibrary("User32.dll");
	if (!hUser32DLL)
		return -1;

	HMODULE hKernel32DLL = LoadLibrary("Kernel32.dll");
	if (!hKernel32DLL)
	{
		FreeLibrary(hUser32DLL);
		return -1;
	}

	RequiredShellcodeData shc_data;
	ZeroMemory(&shc_data, sizeof(RequiredShellcodeData));

	shc_data.hUser32DLL = (DWORD)hUser32DLL;
	shc_data.hKernel32DLL = (DWORD)hKernel32DLL;
	shc_data.dwGetProcAddress = (DWORD)&GetProcAddress;

	int status = execute_shellcode(&shc_data);

	FreeLibrary(hUser32DLL);
	FreeLibrary(hKernel32DLL);
	system("pause");
	return status;
}
