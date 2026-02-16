using System;
using System.Runtime.InteropServices;
using System.Security.Principal;

namespace GoPro.Utils
{
	public static class UACHelper
	{
		internal enum TokenInformationClass
		{
			TokenUser = 1,
			TokenGroups,
			TokenPrivileges,
			TokenOwner,
			TokenPrimaryGroup,
			TokenDefaultDacl,
			TokenSource,
			TokenType,
			TokenImpersonationLevel,
			TokenStatistics,
			TokenRestrictedSids,
			TokenSessionId,
			TokenGroupsAndPrivileges,
			TokenSessionReference,
			TokenSandBoxInert,
			TokenAuditPolicy,
			TokenOrigin,
			TokenElevationType,
			TokenLinkedToken,
			TokenElevation,
			TokenHasRestrictions,
			TokenAccessInformation,
			TokenVirtualizationAllowed,
			TokenVirtualizationEnabled,
			TokenIntegrityLevel,
			TokenUiAccess,
			TokenMandatoryPolicy,
			TokenLogonSid,
			MaxTokenInfoClass
		}

		public enum TokenElevationType
		{
			Default = 1,
			Full,
			Limited
		}

		[DllImport("advapi32.dll", SetLastError = true)]
		internal static extern bool GetTokenInformation(IntPtr tokenHandle, TokenInformationClass tokenInformationClass, IntPtr tokenInformation, int tokenInformationLength, out int returnLength);

		public static TokenElevationType GetTokenElevation()
		{
			WindowsIdentity current = WindowsIdentity.GetCurrent();
			if (current == null)
			{
				return TokenElevationType.Default;
			}
			if (new WindowsPrincipal(current).IsInRole(WindowsBuiltInRole.Administrator))
			{
				return TokenElevationType.Full;
			}
			int returnLength = Marshal.SizeOf(typeof(int));
			IntPtr intPtr = Marshal.AllocHGlobal(returnLength);
			TokenElevationType result = TokenElevationType.Default;
			if (GetTokenInformation(current.Token, TokenInformationClass.TokenElevationType, intPtr, returnLength, out returnLength))
			{
				result = (TokenElevationType)Marshal.ReadInt32(intPtr);
			}
			Marshal.FreeHGlobal(intPtr);
			return result;
		}
	}
}
