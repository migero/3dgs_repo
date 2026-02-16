using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common.math;
using std;

namespace GoPro.Media
{
	public class FrameRateData : IDisposable
	{
		public unsafe Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* mRational;

		public unsafe bool IsZero
		{
			[return: MarshalAs(UnmanagedType.U1)]
			get
			{
				bool num = *(int*)mRational == 0;
				GC.KeepAlive(this);
				return num;
			}
		}

		public unsafe int Denominator => *(int*)((long)(IntPtr)mRational + 4);

		public unsafe int Numerator => *(int*)mRational;

		public unsafe FrameRateData(int numerator, int denominator)
		{
			//IL_0025: Expected I, but got I8
			//IL_004f: Expected I, but got I8
			uint num = 0u;
			base._002Ector();
			if (denominator == 0)
			{
				throw new ArgumentException("illegal zero denominator");
			}
			System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E obj);
			unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E* ptr = _003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cint_0020_0026_002Cint_0020_0026_002C0_003E(&obj, &numerator, &denominator);
			try
			{
				Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* ptr2 = (Rational_003Cint_002Cunsigned_0020int_002C__int64_003E*)(*(ulong*)ptr);
				*(long*)ptr = 0L;
				mRational = ptr2;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::math::Rational<int,unsigned int,__int64>,std::default_delete<common::math::Rational<int,unsigned int,__int64> > >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			if (*(long*)(&obj) != 0L)
			{
				_003CModule_003E.delete((void*)(*(ulong*)(&obj)), 8uL);
			}
			GC.KeepAlive(this);
		}

		public unsafe FrameRateData(Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* other)
		{
			//IL_0026: Expected I, but got I8
			//IL_0050: Expected I, but got I8
			uint num = 0u;
			base._002Ector();
			if (*(int*)((long)(IntPtr)other + 4) == 0)
			{
				throw new ArgumentException("illegal zero denominator");
			}
			System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E obj);
			unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E* ptr = _003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cclass_0020common_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020const_0020_0026_002C0_003E(&obj, other);
			try
			{
				Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* ptr2 = (Rational_003Cint_002Cunsigned_0020int_002C__int64_003E*)(*(ulong*)ptr);
				*(long*)ptr = 0L;
				mRational = ptr2;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::math::Rational<int,unsigned int,__int64>,std::default_delete<common::math::Rational<int,unsigned int,__int64> > >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			if (*(long*)(&obj) != 0L)
			{
				_003CModule_003E.delete((void*)(*(ulong*)(&obj)), 8uL);
			}
			GC.KeepAlive(this);
		}

		public unsafe FrameRateData()
		{
			//IL_000d: Expected I, but got I8
			//IL_0037: Expected I, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E obj);
			unique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E* ptr = _003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002C0_003E(&obj);
			try
			{
				Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* ptr2 = (Rational_003Cint_002Cunsigned_0020int_002C__int64_003E*)(*(ulong*)ptr);
				*(long*)ptr = 0L;
				mRational = ptr2;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::math::Rational<int,unsigned int,__int64>,std::default_delete<common::math::Rational<int,unsigned int,__int64> > >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Amath_003A_003ARational_003Cint_002Cunsigned_0020int_002C__int64_003E_0020_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			if (*(long*)(&obj) != 0L)
			{
				_003CModule_003E.delete((void*)(*(ulong*)(&obj)), 8uL);
			}
			base._002Ector();
		}

		private unsafe void _007EFrameRateData()
		{
			_003CModule_003E.delete(mRational, 8uL);
			GC.KeepAlive(this);
		}

		public unsafe double ToDouble()
		{
			Rational_003Cint_002Cunsigned_0020int_002C__int64_003E* ptr = mRational;
			double result = (double)(*(int*)ptr) / (double)(*(uint*)((long)(IntPtr)ptr + 4));
			GC.KeepAlive(this);
			return result;
		}

		public unsafe override string ToString()
		{
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002Emath_002ERational_003Cint_002Cunsigned_0020int_002C__int64_003E_002Estring(mRational, &obj);
			string result;
			try
			{
				result = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			try
			{
				_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			GC.KeepAlive(this);
			return result;
		}

		protected unsafe virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_003CModule_003E.delete(mRational, 8uL);
				GC.KeepAlive(this);
			}
			else
			{
				base.Finalize();
			}
		}

		public sealed override void Dispose()
		{
			Dispose(A_0: true);
			GC.SuppressFinalize(this);
			GC.KeepAlive(this);
		}
	}
}
