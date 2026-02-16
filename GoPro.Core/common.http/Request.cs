using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using _003FA0x09ed86a0;

namespace common.http
{
	[StructLayout(LayoutKind.Sequential, Size = 360)]
	[UnsafeValueType]
	[NativeCppClass]
	internal struct Request
	{
		private long _003Calignment_0020member_003E;

		[SpecialName]
		public unsafe static void _003CMarshalCopy_003E(Request* A_0, Request* A_1)
		{
			//IL_000a: Expected I4, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out __clr_placement_new_t _clr_placement_new_t);
			// IL initblk instruction
			System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref _clr_placement_new_t, 0, 1);
			__clr_placement_new_t* ptr = &_clr_placement_new_t;
			__clr_placement_new_t _clr_placement_new_t2 = _clr_placement_new_t;
			try
			{
				if (A_0 != null)
				{
					_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bctor_007D(A_0, A_1);
				}
				return;
			}
			catch
			{
				//try-fault
				_003CModule_003E.delete(A_0, A_0, *ptr);
				throw;
			}
		}

		[SpecialName]
		public unsafe static void _003CMarshalDestroy_003E(Request* A_0)
		{
			_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(A_0);
		}
	}
}
