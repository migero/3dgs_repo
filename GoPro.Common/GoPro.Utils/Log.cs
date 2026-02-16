using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading;
using GoPro.Core.Log;

namespace GoPro.Utils
{
	public class Log
	{
		private static readonly string mComponent = "App";

		private static ThreadLocal<Location> mThreadLocalLocation = new ThreadLocal<Location>(() => new Location());

		public static readonly int MaxFiles = 5;

		public static readonly string FileSinkId = "AppFileSink";

		public static void Debug(string message, [CallerFilePath] string sourceFilePath = null, [CallerLineNumber] uint sourceLineNumber = 0u, [CallerMemberName] string sourceMethod = null)
		{
			Logger.debug(mComponent, GetLocation(sourceFilePath, sourceLineNumber, sourceMethod), message);
		}

		public static void Info(string message, [CallerFilePath] string sourceFilePath = null, [CallerLineNumber] uint sourceLineNumber = 0u, [CallerMemberName] string sourceMethod = null)
		{
			Logger.info(mComponent, GetLocation(sourceFilePath, sourceLineNumber, sourceMethod), message);
		}

		public static void Warn(string message, [CallerFilePath] string sourceFilePath = null, [CallerLineNumber] uint sourceLineNumber = 0u, [CallerMemberName] string sourceMethod = null)
		{
			Logger.warn(mComponent, GetLocation(sourceFilePath, sourceLineNumber, sourceMethod), message);
		}

		public static void Error(string message, [CallerFilePath] string sourceFilePath = null, [CallerLineNumber] uint sourceLineNumber = 0u, [CallerMemberName] string sourceMethod = null)
		{
			Logger.error(mComponent, GetLocation(sourceFilePath, sourceLineNumber, sourceMethod), message);
		}

		public static void Exception(string message, Exception ex, [CallerFilePath] string sourceFilePath = null, [CallerLineNumber] uint sourceLineNumber = 0u, [CallerMemberName] string sourceMethod = null)
		{
			Error(GetVerboseExceptionSummary(ex, message), sourceFilePath, sourceLineNumber, sourceMethod);
		}

		public static string GetVerboseExceptionSummary(Exception ex, string message = null)
		{
			StringBuilder stringBuilder = new StringBuilder();
			if (!string.IsNullOrEmpty(message))
			{
				stringBuilder.AppendLine(message);
			}
			stringBuilder.AppendLine("EXCEPTION -------------------------------------------------");
			stringBuilder.AppendLine($"{ex.GetType()}: {ex.Message}");
			stringBuilder.AppendLine(ex.StackTrace);
			for (Exception innerException = ex.InnerException; innerException != null; innerException = innerException.InnerException)
			{
				stringBuilder.AppendLine("INNER EXCEPTION -------------------------------------------");
				stringBuilder.AppendLine($"{innerException.GetType()}: {innerException.Message}");
				stringBuilder.AppendLine(innerException.StackTrace);
			}
			return stringBuilder.ToString();
		}

		private static Location GetLocation(string sourceFilePath, uint sourceLineNumber, string sourceMethod)
		{
			mThreadLocalLocation.Value.File = sourceFilePath;
			mThreadLocalLocation.Value.Method = sourceMethod;
			mThreadLocalLocation.Value.Line = sourceLineNumber;
			return mThreadLocalLocation.Value;
		}

		[Conditional("ENABLE_DEBUG_OUTPUT_LOGGING")]
		private static void LogToDebugOutput(string str)
		{
		}
	}
}
